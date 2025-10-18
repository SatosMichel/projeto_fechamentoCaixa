from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
from app.utils import db_manager, get_current_user
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Por favor, preencha todos os campos.', 'error')
            return render_template('auth/login.html')
        
        # Autenticar usuário
        user_data = db_manager.authenticate_user(username, password)
        
        if user_data:
            # Criar sessão
            session['user_id'] = user_data['id']
            session['user_name'] = user_data['nome']
            session['username'] = user_data['email']
            session['user_level'] = user_data['nivel_acesso']
            session['login_time'] = datetime.now().isoformat()
            session.permanent = True
            
            flash(f'Bem-vindo, {user_data["nome"]}!', 'success')
            
            # Redirecionar baseado no nível
            if user_data['nivel_acesso'] == 'master':
                return redirect(url_for('master.panel'))
            elif user_data['nivel_acesso'] == 'avancado':
                return redirect(url_for('advanced.panel'))
            elif user_data['nivel_acesso'] == 'caixa':
                return redirect(url_for('cashier.flow'))
        else:
            flash('Usuário ou senha inválidos.', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """Logout do usuário"""
    user_name = session.get('user_name', 'Usuário')
    
    # Log da ação se houver usuário logado
    if 'user_id' in session:
        db_manager.log_action(
            session['user_id'], 
            'logout', 
            f'Usuário {session["username"]} fez logout'
        )
    
    # Limpar sessão
    session.clear()
    
    flash(f'Logout realizado com sucesso, {user_name}!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/request-access', methods=['GET', 'POST'])
def request_access():
    """Solicitação de acesso ao sistema"""
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        nivel_acesso = request.form.get('nivel_acesso', '')
        
        # Validações
        errors = []
        
        if not all([nome, username, password, confirm_password]):
            errors.append('Por favor, preencha todos os campos.')
        
        if password != confirm_password:
            errors.append('As senhas não coincidem.')
        
        if len(password) < 6:
            errors.append('A senha deve ter pelo menos 6 caracteres.')
        
        if len(username) < 3:
            errors.append('O nome de usuário deve ter pelo menos 3 caracteres.')
        
        if nivel_acesso not in ['avancado', 'caixa']:
            errors.append('Nível de acesso inválido.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/request_access.html')
        
        # Criar solicitação
        success = db_manager.create_access_request(nome, username, password, nivel_acesso)
        
        if success:
            flash('Solicitação enviada com sucesso! Aguarde a aprovação do administrador.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Erro ao criar solicitação. O nome de usuário pode já existir.', 'error')
    
    return render_template('auth/request_access.html')

@auth_bp.route('/check-session')
def check_session():
    """Endpoint para verificar se sessão está ativa (AJAX)"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': get_current_user()
        })
    else:
        return jsonify({'authenticated': False}), 401