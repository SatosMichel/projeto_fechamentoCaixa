from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from app.utils import login_required, permission_required, get_current_user, db_manager
from datetime import datetime

master_bp = Blueprint('master', __name__)

@master_bp.route('/panel')
@login_required
@permission_required('master')
def panel():
    """Painel administrativo do usuário master"""
    user = get_current_user()
    
    # Buscar estatísticas para o dashboard
    stats = get_admin_stats()
    
    return render_template('master/panel.html', user=user, stats=stats)

@master_bp.route('/requests')
@login_required
@permission_required('master')
def requests():
    """Gerenciar solicitações de acesso"""
    pending_requests = db_manager.get_pending_requests()
    return render_template('master/requests.html', requests=pending_requests)

@master_bp.route('/approve-request/<int:request_id>')
@login_required
@permission_required('master')
def approve_request(request_id):
    """Aprovar solicitação de acesso"""
    user_id = session['user_id']
    
    if db_manager.approve_request(request_id, user_id, True):
        flash('Solicitação aprovada com sucesso!', 'success')
    else:
        flash('Erro ao aprovar solicitação.', 'error')
    
    return redirect(url_for('master.requests'))

@master_bp.route('/reject-request/<int:request_id>')
@login_required
@permission_required('master')
def reject_request(request_id):
    """Rejeitar solicitação de acesso"""
    user_id = session['user_id']
    
    if db_manager.approve_request(request_id, user_id, False):
        flash('Solicitação rejeitada.', 'info')
    else:
        flash('Erro ao rejeitar solicitação.', 'error')
    
    return redirect(url_for('master.requests'))

@master_bp.route('/users')
@login_required
@permission_required('master')
def users():
    """Gerenciar usuários do sistema"""
    users_list = get_all_users()
    return render_template('master/users.html', users=users_list)

@master_bp.route('/toggle-user/<int:user_id>')
@login_required
@permission_required('master')
def toggle_user(user_id):
    """Ativar/desativar usuário"""
    try:
        # Buscar status atual
        result = db_manager.execute_query('SELECT ativo, nome FROM usuarios WHERE id = ?', (user_id,))
        
        if result:
            user_data = result[0]
            new_status = 0 if user_data['ativo'] else 1
            db_manager.execute_update('UPDATE usuarios SET ativo = ? WHERE id = ?', (new_status, user_id))
            
            action = "ativado" if new_status else "desativado"
            flash(f'Usuário {user_data["nome"]} {action} com sucesso!', 'success')
        else:
            flash('Usuário não encontrado.', 'error')
    
    except Exception as e:
        flash(f'Erro ao alterar status do usuário: {e}', 'error')
    
    return redirect(url_for('master.users'))

@master_bp.route('/cashboxes')
@login_required
@permission_required('master')
def cashboxes():
    """Gerenciar caixas do sistema"""
    cashboxes_list = get_all_cashboxes()
    return render_template('master/cashboxes.html', cashboxes=cashboxes_list)

@master_bp.route('/toggle-cashbox/<int:cashbox_id>')
@login_required
@permission_required('master')
def toggle_cashbox(cashbox_id):
    """Ativar/desativar caixa"""
    try:
        # Buscar status atual
        result = db_manager.execute_query('SELECT ativo, nome FROM caixas WHERE id = ?', (cashbox_id,))
        
        if result:
            cashbox_data = result[0]
            new_status = 0 if cashbox_data['ativo'] else 1
            db_manager.execute_update('UPDATE caixas SET ativo = ? WHERE id = ?', (new_status, cashbox_id))
            
            action = "ativado" if new_status else "desativado"
            flash(f'{cashbox_data["nome"]} {action} com sucesso!', 'success')
        else:
            flash('Caixa não encontrado.', 'error')
    
    except Exception as e:
        flash(f'Erro ao alterar status do caixa: {e}', 'error')
    
    return redirect(url_for('master.cashboxes'))

@master_bp.route('/logs')
@login_required
@permission_required('master')
def logs():
    """Visualizar logs do sistema"""
    filter_action = request.args.get('filter', 'todos')
    logs_list = get_system_logs(filter_action)
    return render_template('master/logs.html', logs=logs_list, current_filter=filter_action)

def get_admin_stats():
    """Obter estatísticas para o painel administrativo"""
    try:
        stats = {}
        
        # Total de usuários ativos
        result = db_manager.execute_query('SELECT COUNT(*) as count FROM usuarios WHERE ativo = 1')
        stats['total_users'] = result[0]['count'] if result else 0
        
        # Solicitações pendentes
        result = db_manager.execute_query('SELECT COUNT(*) as count FROM solicitacoes_acesso WHERE status = "pendente"')
        stats['pending_requests'] = result[0]['count'] if result else 0
        
        # Movimentações de hoje
        today = datetime.now().date()
        result = db_manager.execute_query('SELECT COUNT(*) as count FROM movimentacoes_diarias WHERE data = ?', (today,))
        stats['today_movements'] = result[0]['count'] if result else 0
        
        # Movimentações finalizadas hoje
        result = db_manager.execute_query('SELECT COUNT(*) as count FROM movimentacoes_diarias WHERE data = ? AND status = "finalizado"', (today,))
        stats['today_completed'] = result[0]['count'] if result else 0
        
        return stats
        
    except Exception as e:
        print(f"Erro ao obter estatísticas administrativas: {e}")
        return {'total_users': 0, 'pending_requests': 0, 'today_movements': 0, 'today_completed': 0}

def get_all_users():
    """Obter lista de todos os usuários"""
    try:
        result = db_manager.execute_query('''
            SELECT id, nome, usuario, nivel_acesso, ativo, ultimo_login, data_criacao
            FROM usuarios
            ORDER BY nome
        ''')
        
        users = []
        for user in result:
            ultimo_login = "Nunca"
            if user['ultimo_login']:
                ultimo_login = datetime.strptime(user['ultimo_login'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
            
            data_criacao = datetime.strptime(user['data_criacao'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
            
            users.append({
                'id': user['id'],
                'nome': user['nome'],
                'usuario': user['usuario'],
                'nivel_acesso': user['nivel_acesso'],
                'ativo': user['ativo'],
                'ultimo_login': ultimo_login,
                'data_criacao': data_criacao
            })
        
        return users
        
    except Exception as e:
        print(f"Erro ao obter usuários: {e}")
        return []

def get_all_cashboxes():
    """Obter lista de todos os caixas"""
    try:
        result = db_manager.execute_query('''
            SELECT id, nome, ativo, data_criacao
            FROM caixas
            ORDER BY id
        ''')
        
        cashboxes = []
        for cashbox in result:
            data_criacao = datetime.strptime(cashbox['data_criacao'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
            
            cashboxes.append({
                'id': cashbox['id'],
                'nome': cashbox['nome'],
                'ativo': cashbox['ativo'],
                'data_criacao': data_criacao
            })
        
        return cashboxes
        
    except Exception as e:
        print(f"Erro ao obter caixas: {e}")
        return []

def get_system_logs(filter_action='todos'):
    """Obter logs do sistema"""
    try:
        if filter_action == 'todos':
            result = db_manager.execute_query('''
                SELECT l.id, u.nome, l.acao, l.detalhes, l.data_acao
                FROM logs_acoes l
                LEFT JOIN usuarios u ON l.usuario_id = u.id
                ORDER BY l.data_acao DESC
                LIMIT 100
            ''')
        else:
            result = db_manager.execute_query('''
                SELECT l.id, u.nome, l.acao, l.detalhes, l.data_acao
                FROM logs_acoes l
                LEFT JOIN usuarios u ON l.usuario_id = u.id
                WHERE l.acao = ?
                ORDER BY l.data_acao DESC
                LIMIT 100
            ''', (filter_action,))
        
        logs = []
        for log in result:
            data_formatada = datetime.strptime(log['data_acao'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')
            usuario_nome = log['nome'] if log['nome'] else "Sistema"
            
            logs.append({
                'id': log['id'],
                'usuario': usuario_nome,
                'acao': log['acao'],
                'detalhes': log['detalhes'] if log['detalhes'] else "",
                'data_acao': data_formatada
            })
        
        return logs
        
    except Exception as e:
        print(f"Erro ao obter logs: {e}")
        return []