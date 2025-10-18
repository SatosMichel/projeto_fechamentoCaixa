#!/usr/bin/env python3
"""
Script de teste para identificar o problema de login
"""
import sys
import os
import traceback

# Adicionar paths
sys.path.append('.')
sys.path.append('src')

try:
    from app import create_app
    print("✅ Importação do app bem-sucedida")
    
    app = create_app()
    print("✅ Criação do app bem-sucedida")
    
    with app.test_client() as client:
        print("✅ Cliente de teste criado")
        
        # Testar GET na página de login
        response = client.get('/auth/login')
        print(f"GET /auth/login: Status {response.status_code}")
        
        # Testar POST de login
        response = client.post('/auth/login', data={
            'username': 'SUP',
            'password': 'Miguel2@'
        })
        print(f"POST /auth/login: Status {response.status_code}")
        
        if response.status_code == 500:
            print("❌ Erro 500 detectado!")
            print("Response data:", response.get_data(as_text=True)[:500])
        
except Exception as e:
    print(f"❌ Erro capturado: {e}")
    print("Traceback completo:")
    traceback.print_exc()