class AuthManager:
    def __init__(self, db_manager):
        """Inicializa o gerenciador de autenticação"""
        self.db_manager = db_manager
        self.current_user = None
        self.session_data = {}
    
    def login(self, usuario, senha):
        """Realiza login do usuário"""
        user_data = self.db_manager.authenticate_user(usuario, senha)
        if user_data:
            self.current_user = user_data
            self.session_data = {
                'login_time': self.db_manager.datetime.now(),
                'last_activity': self.db_manager.datetime.now()
            }
            return True
        return False
    
    def logout(self):
        """Realiza logout do usuário"""
        if self.current_user:
            self.db_manager.log_action(
                self.current_user['id'], 
                "logout", 
                f"Usuário {self.current_user['usuario']} fez logout"
            )
            self.current_user = None
            self.session_data = {}
    
    def is_authenticated(self):
        """Verifica se há usuário autenticado"""
        return self.current_user is not None
    
    def get_current_user(self):
        """Retorna dados do usuário atual"""
        return self.current_user
    
    def has_permission(self, required_level):
        """Verifica se o usuário tem a permissão necessária"""
        if not self.is_authenticated():
            return False
        
        user_level = self.current_user['nivel_acesso']
        
        # Hierarquia de permissões
        levels = {
            'caixa': 1,
            'avancado': 2,
            'master': 3
        }
        
        return levels.get(user_level, 0) >= levels.get(required_level, 0)
    
    def update_activity(self):
        """Atualiza última atividade do usuário"""
        if self.is_authenticated():
            self.session_data['last_activity'] = self.db_manager.datetime.now()
    
    def create_access_request(self, nome, usuario, senha, nivel_acesso):
        """Cria solicitação de acesso"""
        if nivel_acesso not in ['avancado', 'caixa']:
            return False, "Nível de acesso inválido"
        
        success = self.db_manager.create_access_request(nome, usuario, senha, nivel_acesso)
        if success:
            return True, "Solicitação criada com sucesso"
        else:
            return False, "Erro ao criar solicitação. Usuário pode já existir."