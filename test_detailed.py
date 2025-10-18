#!/usr/bin/env python3
"""
Script de teste específico para capturar erros
"""
import sys
import os
import traceback

# Adicionar paths
sys.path.append('.')
sys.path.append('src')

try:
    from app import create_app
    
    app = create_app()
    
    with app.test_client() as client:
        print("=== TESTE 1: Solicitação de Acesso ===")
        
        # Testar solicitação de acesso
        response = client.post('/auth/request-access', data={
            'nome': 'Teste Usuario',
            'username': 'teste@email.com',
            'password': '123456',
            'confirm_password': '123456',
            'nivel_acesso': 'avancado'
        })
        print(f"POST /auth/request-access: Status {response.status_code}")
        
        if response.status_code == 500:
            print("❌ Erro 500 em request-access!")
            print("Response:", response.get_data(as_text=True)[:1000])
        
        print("\n=== TESTE 2: Login e Redirecionamento ===")
        
        # Testar login
        response = client.post('/auth/login', data={
            'username': 'SUP',
            'password': 'Miguel2@'
        }, follow_redirects=False)
        print(f"POST /auth/login: Status {response.status_code}")
        
        if response.status_code == 302:
            print(f"Redirecionamento para: {response.location}")
            
            # Seguir redirecionamento
            response = client.get(response.location)
            print(f"GET {response.location}: Status {response.status_code}")
            
            if response.status_code == 500:
                print("❌ Erro 500 no redirecionamento!")
                print("Response:", response.get_data(as_text=True)[:1000])
        
except Exception as e:
    print(f"❌ Erro capturado: {e}")
    print("Traceback completo:")
    traceback.print_exc()