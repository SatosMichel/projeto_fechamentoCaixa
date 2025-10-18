#!/usr/bin/env python3
"""
Teste específico para reproduzir os erros de login e solicitação
"""
import sys
import os
import requests
import traceback
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:5000"

def test_login_post():
    """Testar POST de login"""
    try:
        print("=== TESTE LOGIN POST ===")
        
        # Primeiro fazer GET para obter sessão
        session = requests.Session()
        response = session.get(urljoin(BASE_URL, "/auth/login"))
        print(f"GET /auth/login: {response.status_code}")
        
        # Fazer POST de login
        data = {
            'username': 'SUP',
            'password': 'Miguel2@'
        }
        
        response = session.post(urljoin(BASE_URL, "/auth/login"), data=data, allow_redirects=False)
        print(f"POST /auth/login: {response.status_code}")
        
        if response.status_code == 500:
            print("❌ ERRO 500 no login!")
            print("Response text:", response.text[:1000])
            return False
        elif response.status_code == 302:
            print(f"✅ Redirecionamento para: {response.headers.get('Location')}")
            return True
        else:
            print(f"Status inesperado: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição de login: {e}")
        return False

def test_request_access_post():
    """Testar POST de solicitação de acesso"""
    try:
        print("\n=== TESTE SOLICITAÇÃO DE ACESSO ===")
        
        session = requests.Session()
        
        # GET na página primeiro
        response = session.get(urljoin(BASE_URL, "/auth/request-access"))
        print(f"GET /auth/request-access: {response.status_code}")
        
        # POST com dados de teste
        data = {
            'nome': 'Usuario Teste',
            'username': 'teste@teste.com',
            'password': '123456',
            'confirm_password': '123456',
            'nivel_acesso': 'avancado'
        }
        
        response = session.post(urljoin(BASE_URL, "/auth/request-access"), data=data, allow_redirects=False)
        print(f"POST /auth/request-access: {response.status_code}")
        
        if response.status_code == 500:
            print("❌ ERRO 500 na solicitação!")
            print("Response text:", response.text[:1000])
            return False
        elif response.status_code == 302:
            print(f"✅ Redirecionamento para: {response.headers.get('Location')}")
            return True
        else:
            print(f"Status inesperado: {response.status_code}")
            print("Response text:", response.text[:500])
            return False
            
    except Exception as e:
        print(f"❌ Erro na requisição de solicitação: {e}")
        return False

if __name__ == "__main__":
    print("Testando requisições HTTP diretas...")
    
    login_ok = test_login_post()
    access_ok = test_request_access_post()
    
    print(f"\n=== RESULTADO ===")
    print(f"Login: {'✅ OK' if login_ok else '❌ FALHOU'}")
    print(f"Solicitação: {'✅ OK' if access_ok else '❌ FALHOU'}")