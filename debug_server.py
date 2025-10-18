#!/usr/bin/env python3
"""
Teste direto do Flask para capturar erros
"""
import sys
import os

# Adicionar paths
sys.path.append('.')
sys.path.append('src')

from app import create_app

app = create_app()

@app.errorhandler(500)
def handle_500(e):
    import traceback
    print("=" * 50)
    print("ERRO 500 CAPTURADO:")
    print("=" * 50)
    print(traceback.format_exc())
    print("=" * 50)
    return str(e), 500

if __name__ == "__main__":
    print("Iniciando servidor com captura de erros...")
    app.run(host='127.0.0.1', port=5000, debug=True)