from flask import Flask, request, session, redirect, url_for, flash
from functools import wraps
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.database_manager import DatabaseManager

# Instâncias globais
db_manager = DatabaseManager()

def login_required(f):
    """Decorator para rotas que requerem login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def permission_required(required_level):
    """Decorator para rotas que requerem nível específico de permissão"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            
            # Verificar permissão
            user_level = session.get('user_level', '')
            levels = {'caixa': 1, 'avancado': 2, 'master': 3}
            
            if levels.get(user_level, 0) < levels.get(required_level, 0):
                flash('Você não tem permissão para acessar esta página.', 'error')
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Retorna informações do usuário atual da sessão"""
    if 'user_id' in session:
        return {
            'id': session['user_id'],
            'nome': session['user_name'],
            'email': session['username'],
            'nivel_acesso': session['user_level']
        }
    return None

def format_currency(value):
    """Formata valor como moeda brasileira"""
    if value is None:
        value = 0
    return f"R$ {value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

def currency_to_float(currency_str):
    """Converte string de moeda para float"""
    if not currency_str:
        return 0.0
    
    # Remove R$, espaços e pontos de milhares
    clean_str = currency_str.replace('R$', '').replace(' ', '').replace('.', '')
    # Troca vírgula por ponto decimal
    clean_str = clean_str.replace(',', '.')
    
    try:
        return float(clean_str)
    except ValueError:
        return 0.0