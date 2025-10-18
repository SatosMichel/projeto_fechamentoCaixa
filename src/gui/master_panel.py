import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class MasterPanel:
    def __init__(self, auth_manager, db_manager, on_logout):
        """Inicializa painel do usuário master"""
        self.auth_manager = auth_manager
        self.db_manager = db_manager
        self.on_logout = on_logout
        
        self.root = tk.Tk()
        self.root.title("Painel Administrativo - Sistema Brumake")
        self.root.geometry("800x600")
        
        # Centralizar janela
        self.center_window()
        
        # Criar interface
        self.create_widgets()
        
        # Atualizar dados iniciais
        self.refresh_requests()
        self.refresh_users()
        self.refresh_cashboxes()
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Cria os widgets da interface"""
        # Barra superior
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        user_info = self.auth_manager.get_current_user()
        welcome_label = ttk.Label(
            top_frame, 
            text=f"Bem-vindo, {user_info['nome']} (Administrador)",
            font=('Arial', 12, 'bold')
        )
        welcome_label.pack(side=tk.LEFT)
        
        ttk.Button(
            top_frame, 
            text="Logout", 
            command=self.handle_logout
        ).pack(side=tk.RIGHT)
        
        # Notebook (abas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Aba 1: Solicitações de Acesso
        self.create_requests_tab()
        
        # Aba 2: Usuários
        self.create_users_tab()
        
        # Aba 3: Caixas
        self.create_cashboxes_tab()
        
        # Aba 4: Logs
        self.create_logs_tab()
    
    def create_requests_tab(self):
        """Cria aba de solicitações de acesso"""
        requests_frame = ttk.Frame(self.notebook)
        self.notebook.add(requests_frame, text="Solicitações de Acesso")
        
        # Título
        ttk.Label(
            requests_frame, 
            text="Solicitações Pendentes", 
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # Treeview para solicitações
        columns = ('ID', 'Nome', 'Usuário', 'Nível', 'Data Solicitação')
        self.requests_tree = ttk.Treeview(requests_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.requests_tree.heading(col, text=col)
            self.requests_tree.column(col, width=120)
        
        self.requests_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Scrollbar
        requests_scrollbar = ttk.Scrollbar(requests_frame, orient=tk.VERTICAL, command=self.requests_tree.yview)
        self.requests_tree.configure(yscrollcommand=requests_scrollbar.set)
        requests_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botões
        requests_btn_frame = ttk.Frame(requests_frame)
        requests_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            requests_btn_frame, 
            text="Aprovar", 
            command=self.approve_request,
            style="Accent.TButton"
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            requests_btn_frame, 
            text="Rejeitar", 
            command=self.reject_request
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            requests_btn_frame, 
            text="Atualizar", 
            command=self.refresh_requests
        ).pack(side=tk.RIGHT, padx=5)
    
    def create_users_tab(self):
        """Cria aba de usuários"""
        users_frame = ttk.Frame(self.notebook)
        self.notebook.add(users_frame, text="Usuários")
        
        # Título
        ttk.Label(
            users_frame, 
            text="Usuários do Sistema", 
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # Treeview para usuários
        columns = ('ID', 'Nome', 'Usuário', 'Nível', 'Status', 'Último Login')
        self.users_tree = ttk.Treeview(users_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=120)
        
        self.users_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Botões
        users_btn_frame = ttk.Frame(users_frame)
        users_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            users_btn_frame, 
            text="Ativar/Desativar", 
            command=self.toggle_user_status
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            users_btn_frame, 
            text="Atualizar", 
            command=self.refresh_users
        ).pack(side=tk.RIGHT, padx=5)
    
    def create_cashboxes_tab(self):
        """Cria aba de caixas"""
        cashboxes_frame = ttk.Frame(self.notebook)
        self.notebook.add(cashboxes_frame, text="Caixas")
        
        # Título
        ttk.Label(
            cashboxes_frame, 
            text="Gerenciar Caixas", 
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # Treeview para caixas
        columns = ('ID', 'Nome', 'Status', 'Data Criação')
        self.cashboxes_tree = ttk.Treeview(cashboxes_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.cashboxes_tree.heading(col, text=col)
            self.cashboxes_tree.column(col, width=150)
        
        self.cashboxes_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Botões
        cashboxes_btn_frame = ttk.Frame(cashboxes_frame)
        cashboxes_btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            cashboxes_btn_frame, 
            text="Ativar/Desativar", 
            command=self.toggle_cashbox_status
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            cashboxes_btn_frame, 
            text="Atualizar", 
            command=self.refresh_cashboxes
        ).pack(side=tk.RIGHT, padx=5)
    
    def create_logs_tab(self):
        """Cria aba de logs"""
        logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(logs_frame, text="Logs do Sistema")
        
        # Título
        ttk.Label(
            logs_frame, 
            text="Logs de Atividades", 
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # Filtros
        filter_frame = ttk.Frame(logs_frame)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Filtrar por ação:").pack(side=tk.LEFT, padx=5)
        
        self.log_filter_var = tk.StringVar(value='todos')
        log_filter_combo = ttk.Combobox(
            filter_frame, 
            textvariable=self.log_filter_var,
            values=['todos', 'login', 'logout', 'aprovacao', 'criacao_usuario'],
            state='readonly',
            width=15
        )
        log_filter_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            filter_frame, 
            text="Filtrar", 
            command=self.filter_logs
        ).pack(side=tk.LEFT, padx=5)
        
        # Treeview para logs
        columns = ('ID', 'Usuário', 'Ação', 'Detalhes', 'Data/Hora')
        self.logs_tree = ttk.Treeview(logs_frame, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.logs_tree.heading(col, text=col)
            if col == 'Detalhes':
                self.logs_tree.column(col, width=200)
            else:
                self.logs_tree.column(col, width=120)
        
        self.logs_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Botão atualizar
        ttk.Button(
            logs_frame, 
            text="Atualizar Logs", 
            command=self.refresh_logs
        ).pack(pady=10)
    
    def refresh_requests(self):
        """Atualiza lista de solicitações"""
        # Limpar árvore
        for item in self.requests_tree.get_children():
            self.requests_tree.delete(item)
        
        # Buscar solicitações pendentes
        requests = self.db_manager.get_pending_requests()
        
        for request in requests:
            # Formatar data
            data_formatada = datetime.strptime(request[4], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
            
            self.requests_tree.insert('', tk.END, values=(
                request[0],  # ID
                request[1],  # Nome
                request[2],  # Usuário
                request[3].title(),  # Nível
                data_formatada  # Data
            ))
    
    def refresh_users(self):
        """Atualiza lista de usuários"""
        # Limpar árvore
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Buscar usuários
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, nome, usuario, nivel_acesso, ativo, ultimo_login
                FROM usuarios
                ORDER BY nome
            ''')
            
            users = cursor.fetchall()
            
            for user in users:
                ultimo_login = "Nunca"
                if user[5]:
                    ultimo_login = datetime.strptime(user[5], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M')
                
                status = "Ativo" if user[4] else "Inativo"
                
                self.users_tree.insert('', tk.END, values=(
                    user[0],  # ID
                    user[1],  # Nome
                    user[2],  # Usuário
                    user[3].title(),  # Nível
                    status,   # Status
                    ultimo_login  # Último login
                ))
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar usuários: {e}")
        finally:
            conn.close()
    
    def refresh_cashboxes(self):
        """Atualiza lista de caixas"""
        # Limpar árvore
        for item in self.cashboxes_tree.get_children():
            self.cashboxes_tree.delete(item)
        
        # Buscar caixas
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT id, nome, ativo, data_criacao
                FROM caixas
                ORDER BY id
            ''')
            
            cashboxes = cursor.fetchall()
            
            for cashbox in cashboxes:
                data_formatada = datetime.strptime(cashbox[3], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y')
                status = "Ativo" if cashbox[2] else "Inativo"
                
                self.cashboxes_tree.insert('', tk.END, values=(
                    cashbox[0],  # ID
                    cashbox[1],  # Nome
                    status,      # Status
                    data_formatada  # Data criação
                ))
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar caixas: {e}")
        finally:
            conn.close()
    
    def approve_request(self):
        """Aprova solicitação selecionada"""
        selected = self.requests_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma solicitação para aprovar.")
            return
        
        item = self.requests_tree.item(selected[0])
        request_id = item['values'][0]
        usuario_nome = item['values'][1]
        
        if messagebox.askyesno("Confirmar", f"Aprovar solicitação de acesso para {usuario_nome}?"):
            user_id = self.auth_manager.get_current_user()['id']
            if self.db_manager.approve_request(request_id, user_id, True):
                messagebox.showinfo("Sucesso", "Solicitação aprovada com sucesso!")
                self.refresh_requests()
                self.refresh_users()
            else:
                messagebox.showerror("Erro", "Erro ao aprovar solicitação.")
    
    def reject_request(self):
        """Rejeita solicitação selecionada"""
        selected = self.requests_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione uma solicitação para rejeitar.")
            return
        
        item = self.requests_tree.item(selected[0])
        request_id = item['values'][0]
        usuario_nome = item['values'][1]
        
        if messagebox.askyesno("Confirmar", f"Rejeitar solicitação de acesso para {usuario_nome}?"):
            user_id = self.auth_manager.get_current_user()['id']
            if self.db_manager.approve_request(request_id, user_id, False):
                messagebox.showinfo("Sucesso", "Solicitação rejeitada.")
                self.refresh_requests()
            else:
                messagebox.showerror("Erro", "Erro ao rejeitar solicitação.")
    
    def toggle_user_status(self):
        """Ativa/desativa usuário selecionado"""
        selected = self.users_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um usuário.")
            return
        
        item = self.users_tree.item(selected[0])
        user_id = item['values'][0]
        nome = item['values'][1]
        status_atual = item['values'][4]
        
        new_status = 0 if status_atual == "Ativo" else 1
        action = "desativar" if status_atual == "Ativo" else "ativar"
        
        if messagebox.askyesno("Confirmar", f"Deseja {action} o usuário {nome}?"):
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('UPDATE usuarios SET ativo = ? WHERE id = ?', (new_status, user_id))
                conn.commit()
                messagebox.showinfo("Sucesso", f"Usuário {action}do com sucesso!")
                self.refresh_users()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao {action} usuário: {e}")
            finally:
                conn.close()
    
    def toggle_cashbox_status(self):
        """Ativa/desativa caixa selecionado"""
        selected = self.cashboxes_tree.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um caixa.")
            return
        
        item = self.cashboxes_tree.item(selected[0])
        cashbox_id = item['values'][0]
        nome = item['values'][1]
        status_atual = item['values'][2]
        
        new_status = 0 if status_atual == "Ativo" else 1
        action = "desativar" if status_atual == "Ativo" else "ativar"
        
        if messagebox.askyesno("Confirmar", f"Deseja {action} o {nome}?"):
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('UPDATE caixas SET ativo = ? WHERE id = ?', (new_status, cashbox_id))
                conn.commit()
                messagebox.showinfo("Sucesso", f"{nome} {action}do com sucesso!")
                self.refresh_cashboxes()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao {action} caixa: {e}")
            finally:
                conn.close()
    
    def filter_logs(self):
        """Filtra logs por ação"""
        self.refresh_logs()
    
    def refresh_logs(self):
        """Atualiza lista de logs"""
        # Limpar árvore
        for item in self.logs_tree.get_children():
            self.logs_tree.delete(item)
        
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            filter_action = self.log_filter_var.get()
            
            if filter_action == 'todos':
                cursor.execute('''
                    SELECT l.id, u.nome, l.acao, l.detalhes, l.data_acao
                    FROM logs_acoes l
                    LEFT JOIN usuarios u ON l.usuario_id = u.id
                    ORDER BY l.data_acao DESC
                    LIMIT 100
                ''')
            else:
                cursor.execute('''
                    SELECT l.id, u.nome, l.acao, l.detalhes, l.data_acao
                    FROM logs_acoes l
                    LEFT JOIN usuarios u ON l.usuario_id = u.id
                    WHERE l.acao = ?
                    ORDER BY l.data_acao DESC
                    LIMIT 100
                ''', (filter_action,))
            
            logs = cursor.fetchall()
            
            for log in logs:
                data_formatada = datetime.strptime(log[4], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y %H:%M:%S')
                usuario_nome = log[1] if log[1] else "Sistema"
                
                self.logs_tree.insert('', tk.END, values=(
                    log[0],  # ID
                    usuario_nome,  # Nome usuário
                    log[2],  # Ação
                    log[3] if log[3] else "",  # Detalhes
                    data_formatada  # Data/hora
                ))
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar logs: {e}")
        finally:
            conn.close()
    
    def handle_logout(self):
        """Processa logout"""
        if messagebox.askyesno("Logout", "Deseja realmente sair do sistema?"):
            self.auth_manager.logout()
            self.root.destroy()
            self.on_logout()
    
    def run(self):
        """Executa a interface"""
        self.root.mainloop()


if __name__ == "__main__":
    # Teste do painel master
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from database_manager import DatabaseManager
    from auth_manager import AuthManager
    
    db = DatabaseManager()
    auth = AuthManager(db)
    
    # Login como admin para teste
    if auth.login("admin", "admin123"):
        def on_logout():
            print("Logout realizado")
        
        panel = MasterPanel(auth, db, on_logout)
        panel.run()
    else:
        print("Erro no login")