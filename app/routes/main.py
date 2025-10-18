from flask import Blueprint, render_template, session, redirect, url_for
from app.utils import login_required, get_current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página inicial - redireciona para login ou dashboard"""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal baseado no nível do usuário"""
    user = get_current_user()
    
    if user['nivel_acesso'] == 'master':
        return redirect(url_for('master.panel'))
    elif user['nivel_acesso'] == 'avancado':
        return redirect(url_for('advanced.panel'))
    elif user['nivel_acesso'] == 'caixa':
        return redirect(url_for('cashier.flow'))
    else:
        return redirect(url_for('auth.logout'))

@main_bp.route('/about')
def about():
    """Página sobre o sistema"""
    return render_template('about.html')