from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, date, timedelta
import sqlite3
import os
import sys

# Adicionar o diretório pai ao path para importar database_manager
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.database_manager import DatabaseManager

cashier_bp = Blueprint('cashier', __name__, url_prefix='/cashier')

# Decorador para verificar se é operador de caixa
def cashier_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para continuar.', 'warning')
            return redirect(url_for('auth.login'))
        
        if session.get('user_level') not in ['operador_caixa', 'avancado', 'master']:
            flash('Acesso negado. Você não tem permissão para acessar esta área.', 'error')
            return redirect(url_for('main.index'))
        
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@cashier_bp.route('/dashboard')
@cashier_required
def dashboard():
    """Dashboard do operador de caixa"""
    try:
        db = DatabaseManager()
        
        # Verificar se há movimentação em aberto para o usuário
        today = date.today().strftime('%Y-%m-%d')
        
        # Buscar movimentação do dia atual
        query = """
        SELECT * FROM movimentacoes_diarias 
        WHERE usuario_id = ? AND data = ? AND status = 'aberto'
        """
        movimentacao = db.execute_query(query, (session['user_id'], today))
        
        # Buscar dados dos caixas
        caixas = db.execute_query("SELECT * FROM caixas ORDER BY numero")
        
        # Estatísticas do usuário
        stats_query = """
        SELECT 
            COUNT(*) as total_fechamentos,
            SUM(CASE WHEN data >= date('now', '-30 days') THEN 1 ELSE 0 END) as fechamentos_mes,
            AVG(valor_total) as media_valor
        FROM movimentacoes_diarias 
        WHERE usuario_id = ? AND status = 'fechado'
        """
        stats = db.execute_query(stats_query, (session['user_id'],))
        
        return render_template('cashier/dashboard.html', 
                             movimentacao=movimentacao[0] if movimentacao else None,
                             caixas=caixas,
                             stats=stats[0] if stats else None,
                             today=today)
    
    except Exception as e:
        flash(f'Erro ao carregar dashboard: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@cashier_bp.route('/iniciar_caixa', methods=['GET', 'POST'])
@cashier_required
def iniciar_caixa():
    """Iniciar movimentação de caixa"""
    if request.method == 'POST':
        try:
            numero_caixa = request.form.get('numero_caixa')
            valor_inicial = float(request.form.get('valor_inicial', 0))
            observacoes = request.form.get('observacoes', '')
            
            # Validações
            if not numero_caixa:
                flash('Selecione um caixa válido.', 'error')
                return redirect(url_for('cashier.iniciar_caixa'))
            
            if valor_inicial < 0:
                flash('O valor inicial não pode ser negativo.', 'error')
                return redirect(url_for('cashier.iniciar_caixa'))
            
            db = DatabaseManager()
            today = date.today().strftime('%Y-%m-%d')
            
            # Verificar se já existe movimentação aberta para o usuário hoje
            existing = db.execute_query("""
                SELECT id FROM movimentacoes_diarias 
                WHERE usuario_id = ? AND data = ? AND status = 'aberto'
            """, (session['user_id'], today))
            
            if existing:
                flash('Você já possui uma movimentação aberta para hoje.', 'warning')
                return redirect(url_for('cashier.dashboard'))
            
            # Verificar se o caixa já está em uso hoje
            caixa_em_uso = db.execute_query("""
                SELECT u.nome FROM movimentacoes_diarias m
                JOIN usuarios u ON m.usuario_id = u.id
                WHERE m.numero_caixa = ? AND m.data = ? AND m.status = 'aberto'
            """, (numero_caixa, today))
            
            if caixa_em_uso:
                flash(f'Caixa {numero_caixa} já está sendo utilizado por {caixa_em_uso[0]["nome"]}.', 'error')
                return redirect(url_for('cashier.iniciar_caixa'))
            
            # Criar nova movimentação
            query = """
            INSERT INTO movimentacoes_diarias 
            (usuario_id, numero_caixa, data, hora_abertura, valor_inicial, observacoes_abertura, status)
            VALUES (?, ?, ?, ?, ?, ?, 'aberto')
            """
            
            hora_atual = datetime.now().strftime('%H:%M:%S')
            params = (session['user_id'], numero_caixa, today, hora_atual, valor_inicial, observacoes)
            
            if db.execute_update(query, params):
                # Log da ação
                db.log_action(session['user_id'], 'iniciar_caixa', 
                             f'Caixa {numero_caixa} iniciado com R$ {valor_inicial:.2f}')
                
                flash(f'Caixa {numero_caixa} iniciado com sucesso!', 'success')
                return redirect(url_for('cashier.dashboard'))
            else:
                flash('Erro ao iniciar caixa. Tente novamente.', 'error')
        
        except ValueError:
            flash('Valor inicial inválido.', 'error')
        except Exception as e:
            flash(f'Erro ao iniciar caixa: {str(e)}', 'error')
    
    # GET request - mostrar formulário
    try:
        db = DatabaseManager()
        caixas = db.execute_query("SELECT * FROM caixas ORDER BY numero")
        return render_template('cashier/iniciar_caixa.html', caixas=caixas)
    except Exception as e:
        flash(f'Erro ao carregar página: {str(e)}', 'error')
        return redirect(url_for('cashier.dashboard'))

@cashier_bp.route('/fechar_caixa', methods=['GET', 'POST'])
@cashier_required
def fechar_caixa():
    """Fechar movimentação de caixa"""
    try:
        db = DatabaseManager()
        today = date.today().strftime('%Y-%m-%d')
        
        # Buscar movimentação aberta
        movimentacao = db.execute_query("""
            SELECT * FROM movimentacoes_diarias 
            WHERE usuario_id = ? AND data = ? AND status = 'aberto'
        """, (session['user_id'], today))
        
        if not movimentacao:
            flash('Não há movimentação aberta para fechar.', 'warning')
            return redirect(url_for('cashier.dashboard'))
        
        movimentacao = movimentacao[0]
        
        if request.method == 'POST':
            try:
                # Coletar dados do formulário
                vendas_dinheiro = float(request.form.get('vendas_dinheiro', 0))
                vendas_cartao_credito = float(request.form.get('vendas_cartao_credito', 0))
                vendas_cartao_debito = float(request.form.get('vendas_cartao_debito', 0))
                vendas_pix = float(request.form.get('vendas_pix', 0))
                vendas_outros = float(request.form.get('vendas_outros', 0))
                
                sangrias = float(request.form.get('sangrias', 0))
                suprimentos = float(request.form.get('suprimentos', 0))
                dinheiro_caixa = float(request.form.get('dinheiro_caixa', 0))
                
                observacoes = request.form.get('observacoes_fechamento', '')
                
                # Validações
                if any(valor < 0 for valor in [vendas_dinheiro, vendas_cartao_credito, 
                                             vendas_cartao_debito, vendas_pix, vendas_outros,
                                             sangrias, suprimentos, dinheiro_caixa]):
                    flash('Nenhum valor pode ser negativo.', 'error')
                    return render_template('cashier/fechar_caixa.html', movimentacao=movimentacao)
                
                # Calcular totais
                total_vendas = (vendas_dinheiro + vendas_cartao_credito + 
                               vendas_cartao_debito + vendas_pix + vendas_outros)
                
                valor_esperado = (movimentacao['valor_inicial'] + vendas_dinheiro + 
                                 suprimentos - sangrias)
                
                diferenca = dinheiro_caixa - valor_esperado
                valor_total = total_vendas
                
                # Atualizar movimentação
                update_query = """
                UPDATE movimentacoes_diarias SET
                    hora_fechamento = ?,
                    vendas_dinheiro = ?,
                    vendas_cartao_credito = ?,
                    vendas_cartao_debito = ?,
                    vendas_pix = ?,
                    vendas_outros = ?,
                    sangrias = ?,
                    suprimentos = ?,
                    dinheiro_caixa = ?,
                    valor_esperado = ?,
                    diferenca = ?,
                    valor_total = ?,
                    observacoes_fechamento = ?,
                    status = 'fechado'
                WHERE id = ?
                """
                
                hora_atual = datetime.now().strftime('%H:%M:%S')
                params = (
                    hora_atual, vendas_dinheiro, vendas_cartao_credito,
                    vendas_cartao_debito, vendas_pix, vendas_outros,
                    sangrias, suprimentos, dinheiro_caixa, valor_esperado,
                    diferenca, valor_total, observacoes, movimentacao['id']
                )
                
                if db.execute_update(update_query, params):
                    # Log da ação
                    db.log_action(session['user_id'], 'fechar_caixa',
                                 f'Caixa {movimentacao["numero_caixa"]} fechado - Total: R$ {valor_total:.2f}')
                    
                    flash('Caixa fechado com sucesso!', 'success')
                    return redirect(url_for('cashier.relatorio_fechamento', 
                                          movimentacao_id=movimentacao['id']))
                else:
                    flash('Erro ao fechar caixa. Tente novamente.', 'error')
            
            except ValueError:
                flash('Valores inválidos. Verifique os dados informados.', 'error')
            except Exception as e:
                flash(f'Erro ao fechar caixa: {str(e)}', 'error')
        
        return render_template('cashier/fechar_caixa.html', movimentacao=movimentacao)
    
    except Exception as e:
        flash(f'Erro ao carregar página: {str(e)}', 'error')
        return redirect(url_for('cashier.dashboard'))

@cashier_bp.route('/relatorio/<int:movimentacao_id>')
@cashier_required
def relatorio_fechamento(movimentacao_id):
    """Exibir relatório de fechamento"""
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
            return redirect(url_for('cashier.dashboard'))
        
        movimentacao = movimentacao[0]
        
        # Verificar se o usuário pode acessar esta movimentação
        if (movimentacao['usuario_id'] != session['user_id'] and 
            session.get('user_level') not in ['avancado', 'master']):
            flash('Você não tem permissão para acessar este relatório.', 'error')
            return redirect(url_for('cashier.dashboard'))
        
        return render_template('cashier/relatorio.html', movimentacao=movimentacao)
    
    except Exception as e:
        flash(f'Erro ao carregar relatório: {str(e)}', 'error')
        return redirect(url_for('cashier.dashboard'))

@cashier_bp.route('/historico')
@cashier_required
def historico():
    """Histórico de movimentações do operador"""
    try:
        db = DatabaseManager()
        page = request.args.get('page', 1, type=int)
        per_page = 20
        offset = (page - 1) * per_page
        
        # Buscar movimentações do usuário
        query = """
        SELECT m.*, c.nome as caixa_nome
        FROM movimentacoes_diarias m
        JOIN caixas c ON m.numero_caixa = c.numero
        WHERE m.usuario_id = ?
        ORDER BY m.data DESC, m.hora_abertura DESC
        LIMIT ? OFFSET ?
        """
        
        movimentacoes = db.execute_query(query, (session['user_id'], per_page, offset))
        
        # Contar total para paginação
        count_query = """
        SELECT COUNT(*) as total FROM movimentacoes_diarias 
        WHERE usuario_id = ?
        """
        total_count = db.execute_query(count_query, (session['user_id'],))[0]['total']
        
        # Calcular informações de paginação
        total_pages = (total_count + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        return render_template('cashier/historico.html',
                             movimentacoes=movimentacoes,
                             page=page,
                             total_pages=total_pages,
                             has_prev=has_prev,
                             has_next=has_next,
                             total_count=total_count)
    
    except Exception as e:
        flash(f'Erro ao carregar histórico: {str(e)}', 'error')
        return redirect(url_for('cashier.dashboard'))

@cashier_bp.route('/api/status_caixa')
@cashier_required
def api_status_caixa():
    """API para verificar status atual do caixa"""
    try:
        db = DatabaseManager()
        today = date.today().strftime('%Y-%m-%d')
        
        movimentacao = db.execute_query("""
            SELECT * FROM movimentacoes_diarias 
            WHERE usuario_id = ? AND data = ? AND status = 'aberto'
        """, (session['user_id'], today))
        
        return jsonify({
            'success': True,
            'tem_caixa_aberto': len(movimentacao) > 0,
            'movimentacao': movimentacao[0] if movimentacao else None
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@cashier_bp.route('/api/calcular_diferenca', methods=['POST'])
@cashier_required
def api_calcular_diferenca():
    """API para calcular diferença em tempo real"""
    try:
        data = request.get_json()
        
        valor_inicial = float(data.get('valor_inicial', 0))
        vendas_dinheiro = float(data.get('vendas_dinheiro', 0))
        sangrias = float(data.get('sangrias', 0))
        suprimentos = float(data.get('suprimentos', 0))
        dinheiro_caixa = float(data.get('dinheiro_caixa', 0))
        
        valor_esperado = valor_inicial + vendas_dinheiro + suprimentos - sangrias
        diferenca = dinheiro_caixa - valor_esperado
        
        return jsonify({
            'success': True,
            'valor_esperado': valor_esperado,
            'diferenca': diferenca
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500