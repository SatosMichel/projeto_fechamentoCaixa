#!/usr/bin/env python3
"""
Teste específico de redirecionamento após login
"""
import sys
import os
import traceback

sys.path.append('.')
sys.path.append('src')

try:
    from app import create_app
    
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            # Simular sessão de usuário master
            with client.session_transaction() as sess:
                sess['user_id'] = 1
                sess['user_name'] = 'Supervisor'
                sess['username'] = 'SUP'
                sess['user_level'] = 'master'
            
            print("=== TESTE ROTAS ESPECÍFICAS ===")
            
            # Testar rota do master
            try:
                response = client.get('/master/panel')
                print(f"GET /master/panel: {response.status_code}")
                if response.status_code == 500:
                    print("❌ Erro 500 em master/panel")
            except Exception as e:
                print(f"❌ Erro ao acessar master/panel: {e}")
            
            # Testar dashboard principal
            try:
                response = client.get('/dashboard')
                print(f"GET /dashboard: {response.status_code}")
                if response.status_code == 500:
                    print("❌ Erro 500 em dashboard")
            except Exception as e:
                print(f"❌ Erro ao acessar dashboard: {e}")
            
            # Testar página inicial
            try:
                response = client.get('/')
                print(f"GET /: {response.status_code}")
                if response.status_code == 500:
                    print("❌ Erro 500 na página inicial")
            except Exception as e:
                print(f"❌ Erro ao acessar página inicial: {e}")

except Exception as e:
    print(f"❌ Erro geral: {e}")
    traceback.print_exc()