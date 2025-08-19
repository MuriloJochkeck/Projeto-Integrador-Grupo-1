from banco import DataBase

# Instância global do banco
db_instance = DataBase()

def init_database(app):
    """Inicializa o banco de dados"""
    try:
        # Criar banco se não existir
        if not db_instance.criar_banco():
            print(" Falha ao criar banco de dados")
            return False
        
        # Conectar
        if not db_instance.conectar():
            print(" Falha ao conectar ao banco")
            return False
        
        # Criar tabela
        if not db_instance.criar_tabela():
            print(" Falha ao criar tabela")
            return False
        
        print(" Banco de dados inicializado com sucesso!")
        return True
        
    except Exception as e:
        print(f" Erro ao inicializar banco: {e}")
        return False

# Classe Usuario para compatibilidade
class Usuario:
    def __init__(self, id=None, nome=None, telefone=None, cpf=None, email=None, senha=None):
        self.id = id
        self.nome = nome
        self.telefone = telefone
        self.cpf = cpf
        self.email = email
        self.senha = senha
    
    @staticmethod
    def query():
        return UsuarioQuery()
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'telefone': self.telefone,
            'cpf': self.cpf,
            'email': self.email
        }

class UsuarioQuery:
    def filter_by(self, **kwargs):
        self.filters = kwargs
        return self
    
    def first(self):
        # Implementação simples para verificar se usuário existe
        if 'email' in self.filters:
            # Aqui você pode implementar a busca por email se necessário
            return None
        return None

# Instância do banco para uso global
db = db_instance