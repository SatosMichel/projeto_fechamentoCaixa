from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from datetime import datetime, date, timedelta
import sqlite3
import os
import sys
from io import BytesIO
import csv

# Adicionar o diretório pai ao path para importar database_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.database_manager import DatabaseManager

advanced_bp = Blueprint('advanced', __name__, url_prefix='/advanced')

# Decorador para verificar se é usuário avançado
def advanced_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para continuar.', 'warning')
            return redirect(url_for('auth.login'))
        
        if session.get('user_level') not in ['avancado', 'master']:
            flash('Acesso negado. Você não tem permissão para acessar esta área.', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@advanced_bp.route('/dashboard')
@advanced_required
def dashboard():
    """Dashboard do usuário avançado"""
    try:
        db = DatabaseManager()
        
        # Estatísticas gerais
        today = date.today()
        inicio_mes = today.replace(day=1).strftime('%Y-%m-%d')
        
        # Movimentações de hoje
        movimentacoes_hoje = db.execute_query("""
            SELECT m.*, u.nome as operador_nome, c.nome as caixa_nome
            FROM movimentacoes_diarias m
            JOIN usuarios u ON m.usuario_id = u.id
            JOIN caixas c ON m.numero_caixa = c.numero
            WHERE m.data = ?
            ORDER BY m.numero_caixa
        """, (today.strftime('%Y-%m-%d'),))
        
        # Estatísticas do mês
        stats_mes = db.execute_query("""
            SELECT 
                COUNT(*) as total_fechamentos,
                SUM(valor_total) as total_vendas,
                SUM(diferenca) as total_diferencas,
                AVG(valor_total) as media_vendas
            FROM movimentacoes_diarias 
            WHERE data >= ? AND status = 'fechado'
        """, (inicio_mes,))
        
        # Top operadores do mês
        top_operadores = db.execute_query("""
            SELECT 
                u.nome,
                COUNT(*) as total_fechamentos,
                SUM(m.valor_total) as total_vendas,
                AVG(m.valor_total) as media_vendas
            FROM movimentacoes_diarias m
            JOIN usuarios u ON m.usuario_id = u.id
            WHERE m.data >= ? AND m.status = 'fechado'
            GROUP BY u.id, u.nome
            ORDER BY total_vendas DESC
            LIMIT 5
        """, (inicio_mes,))
        
        # Caixas com maiores diferenças
        diferencas_caixas = db.execute_query("""
            SELECT 
                c.nome as caixa_nome,
                m.numero_caixa,
                SUM(ABS(m.diferenca)) as total_diferencas,
                COUNT(*) as total_fechamentos
            FROM movimentacoes_diarias m
            JOIN caixas c ON m.numero_caixa = c.numero
            WHERE m.data >= ? AND m.status = 'fechado'
            GROUP BY m.numero_caixa, c.nome
            ORDER BY total_diferencas DESC
            LIMIT 5
        """, (inicio_mes,))
        
        return render_template('advanced/dashboard.html',
                             movimentacoes_hoje=movimentacoes_hoje,
                             stats_mes=stats_mes[0] if stats_mes else None,
                             top_operadores=top_operadores,
                             diferencas_caixas=diferencas_caixas,
                             today=today)
    
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@advanced_bp.route('/relatorios')
@advanced_required
def relatorios():
    """Página de relatórios avançados"""
    try:
        db = DatabaseManager()
        
        # Parâmetros de filtro
        data_inicio = request.args.get('data_inicio', 
                                     (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
        data_fim = request.args.get('data_fim', date.today().strftime('%Y-%m-%d'))
        numero_caixa = request.args.get('numero_caixa', '')
        usuario_id = request.args.get('usuario_id', '')
        status = request.args.get('status', '')
        
        # Construir query base
        where_conditions = ["m.data BETWEEN ? AND ?"]
        params = [data_inicio, data_fim]
        
        if numero_caixa:
            where_conditions.append("m.numero_caixa = ?")
            params.append(numero_caixa)
        
        if usuario_id:
            where_conditions.append("m.usuario_id = ?")
            params.append(usuario_id)
        
        if status:
            where_conditions.append("m.status = ?")
            params.append(status)
        
        where_clause = " AND ".join(where_conditions)
        
        # Buscar movimentações
        query = f"""
        SELECT 
            m.*,
            u.nome as operador_nome,
            c.nome as caixa_nome
        FROM movimentacoes_diarias m
        JOIN usuarios u ON m.usuario_id = u.id
        JOIN caixas c ON m.numero_caixa = c.numero
        WHERE {where_clause}
        ORDER BY m.data DESC, m.numero_caixa
        """
        
        movimentacoes = db.execute_query(query, params)
        
        # Buscar dados para filtros
        caixas = db.execute_query("SELECT * FROM caixas ORDER BY numero")
        usuarios = db.execute_query("""
            SELECT DISTINCT u.id, u.nome 
            FROM usuarios u 
            JOIN movimentacoes_diarias m ON u.id = m.usuario_id
            ORDER BY u.nome
        """)
        
        # Calcular resumo
        resumo = {
            'total_movimentacoes': len(movimentacoes),
            'total_vendas': sum(m.get('valor_total', 0) or 0 for m in movimentacoes),
            'total_diferencas': sum(abs(m.get('diferenca', 0) or 0) for m in movimentacoes),
            'media_vendas': 0
        }
        
        if resumo['total_movimentacoes'] > 0:
            resumo['media_vendas'] = resumo['total_vendas'] / resumo['total_movimentacoes']
        
        return render_template('advanced/relatorios.html',
                             movimentacoes=movimentacoes,
                             caixas=caixas,
                             usuarios=usuarios,
                             resumo=resumo,
                             filtros={
                                 'data_inicio': data_inicio,
                                 'data_fim': data_fim,
                                 'numero_caixa': numero_caixa,
                                 'usuario_id': usuario_id,
                                 'status': status
                             })
    
    except Exception as e:
        flash(f'Erro ao gerar relatórios: {str(e)}', 'error')
        return redirect(url_for('advanced.dashboard'))

@advanced_bp.route('/movimentacao/<int:movimentacao_id>')
@advanced_required
def detalhe_movimentacao(movimentacao_id):
    """Detalhe de uma movimentação específica"""
    try:
        db = DatabaseManager()
        
        # Buscar movimentação
        movimentacao = db.execute_query("""
            SELECT m.*, u.nome as operador_nome, c.nome as caixa_nome
            FROM movimentacoes_diarias m
            JOIN usuarios u ON m.usuario_id = u.id
            JOIN caixas c ON m.numero_caixa = c.numero
            WHERE m.id = ?
        """, (movimentacao_id,))
        
        if not movimentacao:
            flash('Movimentação não encontrada.', 'error')
            return redirect(url_for('advanced.relatorios'))
        
        return render_template('advanced/detalhe_movimentacao.html', 
                             movimentacao=movimentacao[0])
    
    except Exception as e:
        flash(f'Erro ao carregar movimentação: {str(e)}', 'error')
        return redirect(url_for('advanced.relatorios'))

@advanced_bp.route('/usuarios')
@advanced_required
def usuarios():
    """Gerenciar usuários (apenas visualização para avançado)"""
    try:
        db = DatabaseManager()
        
        # Buscar todos os usuários
        usuarios = db.execute_query("""
            SELECT 
                u.*,
                COUNT(m.id) as total_movimentacoes,
                SUM(CASE WHEN m.data >= date('now', '-30 days') THEN 1 ELSE 0 END) as movimentacoes_mes,
                MAX(m.data) as ultima_movimentacao
            FROM usuarios u
            LEFT JOIN movimentacoes_diarias m ON u.id = m.usuario_id
            GROUP BY u.id
            ORDER BY u.nome
        """)
        
        # Buscar solicitações pendentes
        solicitacoes = db.execute_query("""
            SELECT * FROM solicitacoes_acesso 
            WHERE status = 'pendente'
            ORDER BY data_solicitacao DESC
        """)
        
        return render_template('advanced/usuarios.html',
                             usuarios=usuarios,
                             solicitacoes=solicitacoes)
    
    except Exception as e:
        flash(f'Erro ao carregar usuários: {str(e)}', 'error')
        return redirect(url_for('advanced.dashboard'))

@advanced_bp.route('/configuracoes')
@advanced_required
def configuracoes():
    """Configurações do sistema (visualização apenas)"""
    try:
        db = DatabaseManager()
        
        # Buscar configurações dos caixas
        caixas = db.execute_query("SELECT * FROM caixas ORDER BY numero")
        
        # Logs recentes
        logs = db.execute_query("""
            SELECT l.*, u.nome as usuario_nome
            FROM logs_acoes l
            JOIN usuarios u ON l.usuario_id = u.id
            ORDER BY l.data_hora DESC
            LIMIT 20
        """)
        
        return render_template('advanced/configuracoes.html',
                             caixas=caixas,
                             logs=logs)
    
    except Exception as e:
        flash(f'Erro ao carregar configurações: {str(e)}', 'error')
        return redirect(url_for('advanced.dashboard'))

@advanced_bp.route('/exportar_relatorio')
@advanced_required
def exportar_relatorio():
    """Exportar relatório em CSV"""
    try:
        db = DatabaseManager()
        
        # Parâmetros de filtro (mesmos do relatório)
        data_inicio = request.args.get('data_inicio', 
                                     (date.today() - timedelta(days=30)).strftime('%Y-%m-%d'))
        data_fim = request.args.get('data_fim', date.today().strftime('%Y-%m-%d'))
        numero_caixa = request.args.get('numero_caixa', '')
        usuario_id = request.args.get('usuario_id', '')
        status = request.args.get('status', '')
        
        # Construir query
        where_conditions = ["m.data BETWEEN ? AND ?"]
        params = [data_inicio, data_fim]
        
        if numero_caixa:
            where_conditions.append("m.numero_caixa = ?")
            params.append(numero_caixa)
        
        if usuario_id:
            where_conditions.append("m.usuario_id = ?")
            params.append(usuario_id)
        
        if status:
            where_conditions.append("m.status = ?")
            params.append(status)
        
        where_clause = " AND ".join(where_conditions)
        
        query = f"""
        SELECT 
            m.data,
            m.numero_caixa,
            c.nome as caixa_nome,
            u.nome as operador,
            m.hora_abertura,
            m.hora_fechamento,
            m.valor_inicial,
            m.vendas_dinheiro,
            m.vendas_cartao_credito,
            m.vendas_cartao_debito,
            m.vendas_pix,
            m.vendas_outros,
            m.sangrias,
            m.suprimentos,
            m.dinheiro_caixa,
            m.valor_esperado,
            m.diferenca,
            m.valor_total,
            m.status
        FROM movimentacoes_diarias m
        JOIN usuarios u ON m.usuario_id = u.id
        JOIN caixas c ON m.numero_caixa = c.numero
        WHERE {where_clause}
        ORDER BY m.data DESC, m.numero_caixa
        """
        
        movimentacoes = db.execute_query(query, params)
        
        # Criar arquivo CSV
        output = BytesIO()
        output.write('\ufeff'.encode('utf-8'))  # BOM para UTF-8
        
        writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_ALL)
        
        # Cabeçalho
        headers = [
            'Data', 'Caixa', 'Nome do Caixa', 'Operador', 'Abertura', 'Fechamento',
            'Valor Inicial', 'Vendas Dinheiro', 'Cartão Crédito', 'Cartão Débito',
            'PIX', 'Outros', 'Sangrias', 'Suprimentos', 'Dinheiro Caixa',
            'Valor Esperado', 'Diferença', 'Total Vendas', 'Status'
        ]
        
        writer.writerow(headers)
        
        # Dados
        for mov in movimentacoes:
            row = [
                mov.get('data', ''),
                mov.get('numero_caixa', ''),
                mov.get('caixa_nome', ''),
                mov.get('operador', ''),
                mov.get('hora_abertura', ''),
                mov.get('hora_fechamento', ''),
                f"R$ {mov.get('valor_inicial', 0):.2f}".replace('.', ','),
                f"R$ {mov.get('vendas_dinheiro', 0):.2f}".replace('.', ','),
                f"R$ {mov.get('vendas_cartao_credito', 0):.2f}".replace('.', ','),
                f"R$ {mov.get('vendas_cartao_debito', 0):.2f}".replace('.', ','),
                f"R$ {mov.get('vendas_pix', 0):.2f}".replace('.', ','),
                f"R$ {mov.get('vendas_outros', 0):.2f}".replace('.', ','),
                f"R$ {mov.get('sangrias', 0):.2f}".replace('.', ','),
                f"R$ {mov.get('suprimentos', 0):.2f}".replace('.', ','),
                f"R$ {mov.get('dinheiro_caixa', 0):.2f}".replace('.', ','),
                f"R$ {mov.get('valor_esperado', 0):.2f}".replace('.', ','),
                f"R$ {mov.get('diferenca', 0):.2f}".replace('.', ','),
                f"R$ {mov.get('valor_total', 0):.2f}".replace('.', ','),
                mov.get('status', '')
            ]
            writer.writerow(row)
        
        output.seek(0)
        
        # Nome do arquivo
        filename = f"relatorio_caixas_{data_inicio}_a_{data_fim}.csv"
        
        return send_file(
            BytesIO(output.read()),
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        flash(f'Erro ao exportar relatório: {str(e)}', 'error')
        return redirect(url_for('advanced.relatorios'))

@advanced_bp.route('/api/estatisticas_periodo')
@advanced_required
def api_estatisticas_periodo():
    """API para obter estatísticas de um período"""
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if not data_inicio or not data_fim:
            return jsonify({'success': False, 'error': 'Datas são obrigatórias'}), 400
        
        db = DatabaseManager()
        
        # Estatísticas do período
        stats = db.execute_query("""
            SELECT 
                COUNT(*) as total_fechamentos,
                SUM(valor_total) as total_vendas,
                SUM(diferenca) as total_diferencas,
                AVG(valor_total) as media_vendas,
                COUNT(DISTINCT usuario_id) as total_operadores,
                COUNT(DISTINCT numero_caixa) as total_caixas
            FROM movimentacoes_diarias 
            WHERE data BETWEEN ? AND ? AND status = 'fechado'
        """, (data_inicio, data_fim))
        
        # Vendas por dia
        vendas_por_dia = db.execute_query("""
            SELECT 
                data,
                SUM(valor_total) as total_dia
            FROM movimentacoes_diarias 
            WHERE data BETWEEN ? AND ? AND status = 'fechado'
            GROUP BY data
            ORDER BY data
        """, (data_inicio, data_fim))
        
        # Vendas por caixa
        vendas_por_caixa = db.execute_query("""
            SELECT 
                c.nome as caixa_nome,
                m.numero_caixa,
                SUM(m.valor_total) as total_caixa
            FROM movimentacoes_diarias m
            JOIN caixas c ON m.numero_caixa = c.numero
            WHERE m.data BETWEEN ? AND ? AND m.status = 'fechado'
            GROUP BY m.numero_caixa, c.nome
            ORDER BY total_caixa DESC
        """, (data_inicio, data_fim))
        
        return jsonify({
            'success': True,
            'estatisticas': stats[0] if stats else {},
            'vendas_por_dia': vendas_por_dia,
            'vendas_por_caixa': vendas_por_caixa
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@advanced_bp.route('/api/resumo_operador/<int:usuario_id>')
@advanced_required
def api_resumo_operador(usuario_id):
    """API para obter resumo de um operador"""
    try:
        db = DatabaseManager()
        
        # Dados do operador
        operador = db.execute_query("""
            SELECT nome, email, nivel_acesso, data_criacao
            FROM usuarios WHERE id = ?
        """, (usuario_id,))
        
        if not operador:
            return jsonify({'success': False, 'error': 'Operador não encontrado'}), 404
        
        # Estatísticas do operador
        stats = db.execute_query("""
            SELECT 
                COUNT(*) as total_fechamentos,
                SUM(valor_total) as total_vendas,
                AVG(valor_total) as media_vendas,
                SUM(ABS(diferenca)) as total_diferencas,
                MIN(data) as primeira_movimentacao,
                MAX(data) as ultima_movimentacao
            FROM movimentacoes_diarias 
            WHERE usuario_id = ? AND status = 'fechado'
        """, (usuario_id,))
        
        # Atividade por mês (últimos 6 meses)
        atividade_mensal = db.execute_query("""
            SELECT 
                strftime('%Y-%m', data) as mes,
                COUNT(*) as total_fechamentos,
                SUM(valor_total) as total_vendas
            FROM movimentacoes_diarias 
            WHERE usuario_id = ? AND status = 'fechado'
                AND data >= date('now', '-6 months')
            GROUP BY strftime('%Y-%m', data)
            ORDER BY mes
        """, (usuario_id,))
        
        return jsonify({
            'success': True,
            'operador': operador[0],
            'estatisticas': stats[0] if stats else {},
            'atividade_mensal': atividade_mensal
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500