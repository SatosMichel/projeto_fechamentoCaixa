from flask import Flask
from flask_session import Session
import os
from datetime import timedelta

def create_app():
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configurações da aplicação
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'brumake-caixa-secret-key-2025')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    app.config['SESSION_COOKIE_SECURE'] = False  # Mudar para True em produção com HTTPS
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)  # Sessão expira em 8 horas
    
    # Configurações do banco de dados
    app.config['DATABASE_PATH'] = os.path.join(os.getcwd(), 'database', 'brumake_caixa.db')
    app.config['REPORTS_PATH'] = os.path.join(os.getcwd(), 'reports')
    
    # Inicializar extensões
    Session(app)
    
    # Adicionar filtros personalizados ao Jinja2
    from datetime import datetime
    
    @app.template_filter('dateformat')
    def dateformat(value, format='%d/%m/%Y'):
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except:
                return value
        return value.strftime(format)
    
    # Adicionar variáveis globais aos templates
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}
    
    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.master import master_bp
    from app.routes.cashier import cashier_bp
    from app.routes.advanced import advanced_bp
    from app.routes.main import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(master_bp, url_prefix='/master')
    app.register_blueprint(cashier_bp, url_prefix='/cashier')
    app.register_blueprint(advanced_bp, url_prefix='/advanced')
    
    # Garantir que diretórios existem
    os.makedirs(os.path.dirname(app.config['DATABASE_PATH']), exist_ok=True)
    os.makedirs(app.config['REPORTS_PATH'], exist_ok=True)
    
    return app