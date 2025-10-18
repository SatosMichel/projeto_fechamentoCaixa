#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Fechamento de Caixa - Brumake
Arquivo principal do sistema
"""

import tkinter as tk
from tkinter import messagebox
import sys
import os

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importações dos módulos do sistema
from database_manager import DatabaseManager
from auth_manager import AuthManager
from gui.login_window import LoginWindow
from gui.master_panel import MasterPanel
from gui.cashier_flow import CashierFlow
from gui.advanced_panel import AdvancedPanel

class BrumakeCashSystem:
    def __init__(self):
        """Inicializa o sistema principal"""
        print("Inicializando Sistema de Fechamento de Caixa - Brumake...")
        
        # Inicializar componentes
        self.db_manager = None
        self.auth_manager = None
        self.current_window = None
        
        # Configurar sistema
        self.setup_system()
    
    def setup_system(self):
        """Configura os componentes do sistema"""
        try:
            # Inicializar banco de dados
            print("Configurando banco de dados...")
            self.db_manager = DatabaseManager()
            
            # Inicializar gerenciador de autenticação
            self.auth_manager = AuthManager(self.db_manager)
            
            print("Sistema inicializado com sucesso!")
            print("=" * 50)
            print("INFORMAÇÕES IMPORTANTES:")
            print("• Usuário master padrão: admin")
            print("• Senha master padrão: admin123")
            print("• Altere a senha padrão após o primeiro acesso!")
            print("=" * 50)
            
        except Exception as e:
            messagebox.showerror(
                "Erro de Inicialização", 
                f"Erro ao inicializar o sistema:\n{e}\n\nO programa será encerrado."
            )
            sys.exit(1)
    
    def start(self):
        """Inicia o sistema com tela de login"""
        self.show_login()
    
    def show_login(self):
        """Mostra tela de login"""
        if self.current_window:
            try:
                self.current_window.destroy()
            except:
                pass
        
        self.current_window = LoginWindow(self.auth_manager, self.on_login_success)
        self.current_window.run()
    
    def on_login_success(self):
        """Callback executado após login bem-sucedido"""
        if not self.auth_manager.is_authenticated():
            return
        
        user = self.auth_manager.get_current_user()
        user_level = user['nivel_acesso']
        
        print(f"Login realizado: {user['nome']} ({user_level})")
        
        # Fechar janela de login
        if self.current_window:
            self.current_window.destroy()
        
        # Redirecionar baseado no nível de acesso
        if user_level == 'master':
            self.show_master_panel()
        elif user_level == 'avancado':
            self.show_advanced_panel()
        elif user_level == 'caixa':
            self.show_cashier_flow()
        else:
            messagebox.showerror("Erro", "Nível de acesso inválido.")
            self.show_login()
    
    def show_master_panel(self):
        """Mostra painel do usuário master"""
        self.current_window = MasterPanel(
            self.auth_manager, 
            self.db_manager, 
            self.on_logout
        )
        self.current_window.run()
    
    def show_advanced_panel(self):
        """Mostra painel do usuário avançado"""
        self.current_window = AdvancedPanel(
            self.auth_manager, 
            self.db_manager, 
            self.on_logout
        )
        self.current_window.run()
    
    def show_cashier_flow(self):
        """Mostra fluxo do usuário caixa"""
        self.current_window = CashierFlow(
            self.auth_manager, 
            self.db_manager, 
            self.on_logout
        )
        self.current_window.run()
    
    def on_logout(self):
        """Callback executado após logout"""
        print("Logout realizado. Retornando à tela de login...")
        self.show_login()
    
    def shutdown(self):
        """Encerra o sistema de forma segura"""
        if self.auth_manager and self.auth_manager.is_authenticated():
            self.auth_manager.logout()
        
        if self.current_window:
            try:
                self.current_window.destroy()
            except:
                pass
        
        print("Sistema encerrado.")


def main():
    """Função principal"""
    try:
        # Verificar se está sendo executado em ambiente gráfico
        root = tk.Tk()
        root.withdraw()  # Ocultar janela principal temporariamente
        
        # Criar e iniciar sistema
        system = BrumakeCashSystem()
        system.start()
        
    except tk.TclError:
        print("ERRO: Sistema requer ambiente gráfico (GUI)")
        print("Certifique-se de que está executando em um ambiente com suporte gráfico.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nSistema interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"ERRO FATAL: {e}")
        messagebox.showerror("Erro Fatal", f"Erro não tratado:\n{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()