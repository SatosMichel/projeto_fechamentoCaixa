import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Adicionar o diretório src ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class LoginWindow:
    def __init__(self, auth_manager, on_login_success):
        """Inicializa a janela de login"""
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success
        
        self.root = tk.Tk()
        self.root.title("Sistema Fechamento de Caixa - Brumake")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        # Centralizar janela
        self.center_window()
        
        # Configurar estilo
        self.setup_styles()
        
        # Criar interface
        self.create_widgets()
        
        # Foco inicial no campo usuário
        self.entry_usuario.focus()
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_styles(self):
        """Configura estilos da interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores
        self.root.configure(bg='#f0f0f0')
    
    def create_widgets(self):
        """Cria os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Sistema de Fechamento de Caixa", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(
            main_frame, 
            text="BRUMAKE COMERCIAL E SERVIÇOS LTDA", 
            font=('Arial', 10)
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Frame de login
        login_frame = ttk.LabelFrame(main_frame, text="Login", padding="20")
        login_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Campo usuário
        ttk.Label(login_frame, text="Usuário:").pack(anchor=tk.W)
        self.entry_usuario = ttk.Entry(login_frame, font=('Arial', 10))
        self.entry_usuario.pack(fill=tk.X, pady=(5, 15))
        
        # Campo senha
        ttk.Label(login_frame, text="Senha:").pack(anchor=tk.W)
        self.entry_senha = ttk.Entry(login_frame, show="*", font=('Arial', 10))
        self.entry_senha.pack(fill=tk.X, pady=(5, 20))
        
        # Botão entrar
        btn_entrar = ttk.Button(
            login_frame, 
            text="Entrar", 
            command=self.handle_login,
            style="Accent.TButton"
        )
        btn_entrar.pack(fill=tk.X, pady=(0, 10))
        
        # Botão solicitar acesso
        btn_solicitar = ttk.Button(
            login_frame, 
            text="Solicitar Acesso", 
            command=self.open_access_request
        )
        btn_solicitar.pack(fill=tk.X)
        
        # Bind Enter key para login
        self.root.bind('<Return>', lambda event: self.handle_login())
        
        # Label de status
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(10, 0))
    
    def handle_login(self):
        """Processa tentativa de login"""
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()
        
        if not usuario or not senha:
            self.show_status("Por favor, preencha todos os campos.", "error")
            return
        
        # Tentar autenticar
        if self.auth_manager.login(usuario, senha):
            self.show_status("Login realizado com sucesso!", "success")
            self.root.after(1000, self.on_login_success)  # Delay para mostrar mensagem
        else:
            self.show_status("Usuário ou senha inválidos.", "error")
            self.entry_senha.delete(0, tk.END)
            self.entry_usuario.focus()
    
    def show_status(self, message, status_type="info"):
        """Mostra mensagem de status"""
        colors = {
            "success": "green",
            "error": "red",
            "info": "blue"
        }
        
        self.status_label.config(
            text=message, 
            foreground=colors.get(status_type, "black")
        )
    
    def open_access_request(self):
        """Abre janela de solicitação de acesso"""
        AccessRequestWindow(self.auth_manager, self.root)
    
    def run(self):
        """Executa a interface"""
        self.root.mainloop()
    
    def destroy(self):
        """Fecha a janela"""
        self.root.destroy()


class AccessRequestWindow:
    def __init__(self, auth_manager, parent):
        """Inicializa janela de solicitação de acesso"""
        self.auth_manager = auth_manager
        
        self.window = tk.Toplevel(parent)
        self.window.title("Solicitar Acesso ao Sistema")
        self.window.geometry("450x400")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        # Centralizar janela
        self.center_window()
        
        # Criar interface
        self.create_widgets()
    
    def center_window(self):
        """Centraliza a janela na tela"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Cria os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_label = ttk.Label(
            main_frame, 
            text="Solicitação de Acesso", 
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Campos do formulário
        ttk.Label(main_frame, text="Nome completo:").pack(anchor=tk.W)
        self.entry_nome = ttk.Entry(main_frame, font=('Arial', 10))
        self.entry_nome.pack(fill=tk.X, pady=(5, 15))
        
        ttk.Label(main_frame, text="Nome de usuário:").pack(anchor=tk.W)
        self.entry_usuario = ttk.Entry(main_frame, font=('Arial', 10))
        self.entry_usuario.pack(fill=tk.X, pady=(5, 15))
        
        ttk.Label(main_frame, text="Senha:").pack(anchor=tk.W)
        self.entry_senha = ttk.Entry(main_frame, show="*", font=('Arial', 10))
        self.entry_senha.pack(fill=tk.X, pady=(5, 15))
        
        ttk.Label(main_frame, text="Confirmar senha:").pack(anchor=tk.W)
        self.entry_confirmar_senha = ttk.Entry(main_frame, show="*", font=('Arial', 10))
        self.entry_confirmar_senha.pack(fill=tk.X, pady=(5, 15))
        
        ttk.Label(main_frame, text="Tipo de acesso:").pack(anchor=tk.W)
        self.nivel_var = tk.StringVar(value="caixa")
        
        nivel_frame = ttk.Frame(main_frame)
        nivel_frame.pack(fill=tk.X, pady=(5, 20))
        
        ttk.Radiobutton(
            nivel_frame, 
            text="Usuário Caixa", 
            variable=self.nivel_var, 
            value="caixa"
        ).pack(anchor=tk.W)
        
        ttk.Radiobutton(
            nivel_frame, 
            text="Usuário Avançado", 
            variable=self.nivel_var, 
            value="avancado"
        ).pack(anchor=tk.W)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(
            button_frame, 
            text="Cancelar", 
            command=self.window.destroy
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame, 
            text="Solicitar", 
            command=self.handle_request,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT)
        
        # Label de status
        self.status_label = ttk.Label(main_frame, text="", foreground="red")
        self.status_label.pack(pady=(10, 0))
        
        # Foco inicial
        self.entry_nome.focus()
    
    def handle_request(self):
        """Processa solicitação de acesso"""
        nome = self.entry_nome.get().strip()
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()
        confirmar_senha = self.entry_confirmar_senha.get().strip()
        nivel = self.nivel_var.get()
        
        # Validações
        if not all([nome, usuario, senha, confirmar_senha]):
            self.show_status("Por favor, preencha todos os campos.")
            return
        
        if senha != confirmar_senha:
            self.show_status("As senhas não coincidem.")
            return
        
        if len(senha) < 6:
            self.show_status("A senha deve ter pelo menos 6 caracteres.")
            return
        
        if len(usuario) < 3:
            self.show_status("O nome de usuário deve ter pelo menos 3 caracteres.")
            return
        
        # Criar solicitação
        success, message = self.auth_manager.create_access_request(nome, usuario, senha, nivel)
        
        if success:
            messagebox.showinfo(
                "Sucesso", 
                "Solicitação enviada com sucesso!\n\n"
                "Aguarde a aprovação do administrador para acessar o sistema."
            )
            self.window.destroy()
        else:
            self.show_status(message)
    
    def show_status(self, message):
        """Mostra mensagem de status"""
        self.status_label.config(text=message, foreground="red")


if __name__ == "__main__":
    # Teste da janela de login
    from database_manager import DatabaseManager
    from auth_manager import AuthManager
    
    db = DatabaseManager()
    auth = AuthManager(db)
    
    def on_success():
        print(f"Login realizado com sucesso! Usuário: {auth.get_current_user()}")
    
    login_window = LoginWindow(auth, on_success)
    login_window.run()