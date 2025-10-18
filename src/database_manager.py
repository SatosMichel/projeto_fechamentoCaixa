import sqlite3
import hashlib
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="database/brumake_caixa.db"):
        """Inicializa o gerenciador do banco de dados"""
        self.db_path = db_path
        self.ensure_database_directory()
        self.init_database()
    
    def ensure_database_directory(self):
        """Garante que o diretório do banco de dados existe"""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def get_connection(self):
        """Retorna uma conexão com o banco de dados"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicializa todas as tabelas do banco de dados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Tabela de usuários
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    senha TEXT NOT NULL,
                    nivel_acesso TEXT NOT NULL CHECK (nivel_acesso IN ('master', 'avancado', 'operador_caixa')),
                    ativo BOOLEAN DEFAULT 1,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ultimo_login DATETIME
                )
            ''')
            
            # Tabela de caixas disponíveis
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS caixas (
                    numero INTEGER PRIMARY KEY,
                    nome TEXT NOT NULL,
                    descricao TEXT,
                    ativo BOOLEAN DEFAULT 1,
                    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabela de solicitações de acesso
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS solicitacoes_acesso (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    email TEXT NOT NULL,
                    senha TEXT NOT NULL,
                    nivel_solicitado TEXT NOT NULL,
                    status TEXT DEFAULT 'pendente' CHECK (status IN ('pendente', 'aprovado', 'rejeitado')),
                    data_solicitacao DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data_resposta DATETIME,
                    aprovado_por INTEGER,
                    FOREIGN KEY (aprovado_por) REFERENCES usuarios (id)
                )
            ''')
            
            # Tabela de movimentações diárias
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movimentacoes_diarias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER NOT NULL,
                    numero_caixa INTEGER NOT NULL,
                    data DATE NOT NULL,
                    hora_abertura TIME,
                    hora_fechamento TIME,
                    valor_inicial DECIMAL(10,2) DEFAULT 0,
                    vendas_dinheiro DECIMAL(10,2) DEFAULT 0,
                    vendas_cartao_credito DECIMAL(10,2) DEFAULT 0,
                    vendas_cartao_debito DECIMAL(10,2) DEFAULT 0,
                    vendas_pix DECIMAL(10,2) DEFAULT 0,
                    vendas_outros DECIMAL(10,2) DEFAULT 0,
                    sangrias DECIMAL(10,2) DEFAULT 0,
                    suprimentos DECIMAL(10,2) DEFAULT 0,
                    dinheiro_caixa DECIMAL(10,2) DEFAULT 0,
                    valor_esperado DECIMAL(10,2) DEFAULT 0,
                    diferenca DECIMAL(10,2) DEFAULT 0,
                    valor_total DECIMAL(10,2) DEFAULT 0,
                    observacoes_abertura TEXT,
                    observacoes_fechamento TEXT,
                    status TEXT DEFAULT 'aberto' CHECK (status IN ('aberto', 'fechado')),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
                    FOREIGN KEY (numero_caixa) REFERENCES caixas (numero)
                )
            ''')
            
            # Tabela de logs de ações
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs_acoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER,
                    acao TEXT NOT NULL,
                    detalhes TEXT,
                    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            conn.commit()
            print("Banco de dados inicializado com sucesso!")
            
        except Exception as e:
            print(f"Erro ao inicializar banco de dados: {e}")
        finally:
            conn.close()
    
    def execute_query(self, query, params=None):
        """Executa uma query SELECT e retorna os resultados"""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row  # Para acessar colunas por nome
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            results = cursor.fetchall()
            # Converter Row objects para dict
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Erro ao executar query: {e}")
            return []
        finally:
            conn.close()
    
    def execute_update(self, query, params=None):
        """Executa uma query INSERT/UPDATE/DELETE e retorna sucesso"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao executar update: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def log_action(self, user_id, action, details):
        """Registra uma ação no log do sistema"""
        query = """
        INSERT INTO logs_acoes (usuario_id, acao, detalhes, data_hora)
        VALUES (?, ?, ?, ?)
        """
        return self.execute_update(query, (user_id, action, details, datetime.now()))
    
    def setup_database(self):
        """Configuração inicial do banco com dados padrão"""
        # Inserir caixas padrão
        caixas_default = [
            (1, 'Caixa Principal'),
            (2, 'Caixa Secundário'),
            (3, 'Caixa Express'),
            (4, 'Caixa Balcão')
        ]
        
        for numero, nome in caixas_default:
            self.execute_update("""
                INSERT OR IGNORE INTO caixas (numero, nome) VALUES (?, ?)
            """, (numero, nome))
        
        return True

    def authenticate_user(self, username, password):
        """Autentica um usuário"""
        try:
            # Buscar usuário por email (que serve como username)
            result = self.execute_query(
                'SELECT id, nome, email, nivel_acesso, ativo FROM usuarios WHERE email = ? AND senha = ? AND ativo = 1',
                (username, password)
            )
            
            if result:
                user_data = result[0]
                # Atualizar último login
                self.execute_update(
                    'UPDATE usuarios SET ultimo_login = ? WHERE id = ?',
                    (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user_data['id'])
                )
                return user_data
            return None
            
        except Exception as e:
            print(f"Erro na autenticação: {e}")
            return None
    
    def create_access_request(self, nome, username, password, nivel_acesso):
        """Criar solicitação de acesso"""
        try:
            # Verificar se já existe usuário com esse email
            existing = self.execute_query('SELECT id FROM usuarios WHERE email = ?', (username,))
            if existing:
                return False
            
            # Verificar se já existe solicitação pendente
            pending = self.execute_query(
                'SELECT id FROM solicitacoes_acesso WHERE email = ? AND status = "pendente"',
                (username,)
            )
            if pending:
                return False
            
            # Criar solicitação
            self.execute_update('''
                INSERT INTO solicitacoes_acesso (nome, email, senha, nivel_solicitado, status, data_solicitacao)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (nome, username, password, nivel_acesso, 'pendente', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            return True
            
        except Exception as e:
            print(f"Erro ao criar solicitação: {e}")
            return False
    
    def get_pending_requests(self):
        """Obter solicitações de acesso pendentes"""
        try:
            return self.execute_query('''
                SELECT id, nome, email, nivel_solicitado, data_solicitacao
                FROM solicitacoes_acesso
                WHERE status = "pendente"
                ORDER BY data_solicitacao DESC
            ''')
        except Exception as e:
            print(f"Erro ao obter solicitações: {e}")
            return []

# Inicializar banco de dados ao importar o módulo
if __name__ == "__main__":
    db = DatabaseManager()
    print("Banco de dados inicializado!")
    print("Usuário master padrão: SUP / senha: Miguel2@")