#!/usr/bin/env python3
"""
Script de teste específico para capturar erros - versão simples
"""
import sys
import os
import traceback

# Adicionar paths
sys.path.append('.')
sys.path.append('src')

def test_database():
    """Testar operações do banco diretamente"""
    try:
        from src.database_manager import DatabaseManager
        
        db = DatabaseManager()
        print("✅ DatabaseManager criado com sucesso")
        
        # Testar autenticação
        result = db.authenticate_user('SUP', 'Miguel2@')
        print(f"Teste autenticação SUP: {result}")
        
        # Testar criação de solicitação
        result = db.create_access_request('Teste', 'teste@test.com', '123456', 'avancado')
        print(f"Teste criar solicitação: {result}")
        
        # Testar buscar solicitações
        requests = db.get_pending_requests()
        print(f"Solicitações pendentes: {len(requests) if requests else 0}")
        
    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        traceback.print_exc()

def test_routes():
    """Testar rotas individualmente"""
    try:
        from app import create_app
        
        app = create_app()
        print("✅ App criado com sucesso")
        
        with app.test_client() as client:
            with app.app_context():
                # Testar página de login
                response = client.get('/auth/login')
                print(f"GET /auth/login: {response.status_code}")
                
                # Testar página de solicitação
                response = client.get('/auth/request-access')
                print(f"GET /auth/request-access: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Erro nas rotas: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("=== TESTE DO BANCO ===")
    test_database()
    
    print("\n=== TESTE DAS ROTAS ===")  
    test_routes()