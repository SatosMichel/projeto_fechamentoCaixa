from app import create_app
import os
import sys

# Adicionar o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importar e inicializar o banco de dados
from src.database_manager import DatabaseManager

def setup_database():
    """Configurar e inicializar o banco de dados"""
    try:
        db = DatabaseManager()
        
        # Verificar se o banco já existe e tem dados
        tables = db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        
        if not tables:
            print("Inicializando banco de dados...")
            db.setup_database()
            print("Banco de dados configurado com sucesso!")
        else:
            print("Banco de dados já configurado.")
            
        # Verificar se existe usuário master
        master_users = db.execute_query("""
            SELECT COUNT(*) as count FROM usuarios WHERE nivel_acesso = 'master'
        """)
        
        if master_users[0]['count'] == 0:
            print("Criando usuário master padrão...")
            # Criar usuário master padrão
            db.execute_update("""
                INSERT INTO usuarios (nome, email, senha, nivel_acesso, ativo)
                VALUES (?, ?, ?, ?, ?)
            """, ('Supervisor', 'SUP', 'Miguel2@', 'master', 1))
            print("Usuário master criado: SUP / Miguel2@")
        
        return True
        
    except Exception as e:
        print(f"Erro ao configurar banco de dados: {e}")
        return False

def main():
    """Função principal da aplicação"""
    print("=" * 60)
    print("🏢 SISTEMA DE FECHAMENTO DE CAIXA - BRUMAKE")
    print("=" * 60)
    
    # Configurar banco de dados
    if not setup_database():
        print("❌ Erro na configuração do banco de dados. Encerrando...")
        return
    
    # Criar aplicação Flask
    app = create_app()
    
    # Configurações de desenvolvimento
    if os.environ.get('FLASK_ENV') == 'development':
        print("\n🔧 Modo de Desenvolvimento Ativo")
        print("📁 Debug: Habilitado")
        print("🔄 Auto-reload: Habilitado")
    
    # Informações do sistema
    print("\n📋 INFORMAÇÕES DO SISTEMA:")
    print(f"🌐 URL: http://localhost:5000")
    print(f"📊 Dashboard: http://localhost:5000/")
    print(f"🔐 Login: http://localhost:5000/auth/login")
    print(f"📁 Banco de Dados: {app.config['DATABASE_PATH']}")
    print(f"📄 Relatórios: {app.config['REPORTS_PATH']}")
    
    print("\n👥 NÍVEIS DE USUÁRIO:")
    print("🔴 Master: Acesso completo ao sistema")
    print("🟡 Avançado: Relatórios e consultas avançadas")
    print("🟢 Operador: Operações básicas de caixa")
    
    print("\n🚀 INICIANDO SERVIDOR...")
    print("💡 Pressione Ctrl+C para parar o servidor")
    print("=" * 60)
    
    try:
        # Executar aplicação
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=False,
            use_reloader=False
        )
    except KeyboardInterrupt:
        print("\n\n⏹️  Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao executar servidor: {e}")
    finally:
        print("🔚 Encerrando Sistema Brumake...")

if __name__ == '__main__':
    main()