import psycopg2
import hashlib
import json

class banco:
    def __init__(self):
        # Configurações
        self.host = 'localhost'
        self.port = 5432
        self.database = 'projeto_integrador'
        self.user = 'postgres'
        self.password = '1234'
        self.connection = None
    
    def conectar(self):
        """Conecta ao PostgreSQL"""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print(" Conectado ao PostgreSQL!")
            return True
        except Exception as e:
            print(f" Erro ao conectar: {e}")
            return False
    
    def criar_banco(self):
        """Cria o banco de dados"""
        try:
            # Conectar ao banco postgres padrão
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database='projeto_integrador',
                user=self.user,
                password=self.password
            )
            conn.autocommit = True
            cursor = conn.cursor()
            
            # Verificar se o banco existe
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.database,))
            if not cursor.fetchone():
                cursor.execute(f"CREATE DATABASE {self.database}")
                print(f" Banco '{self.database}' criado!")
            
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            print(f" Erro ao criar banco: {e}")
            return False
            
                
    def criar_tabela(self):
        """Cria a tabela de usuários"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    telefone VARCHAR(20) NOT NULL,
                    cpf VARCHAR(14) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    senha VARCHAR(200) NOT NULL,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maquinas (
                    id SERIAL PRIMARY KEY,
                    cep VARCHAR(10) NOT NULL,
                    uf CHAR(2) NOT NULL,
                    numero INTEGER NOT NULL,
                    cidade VARCHAR(50) NOT NULL,
                    rua VARCHAR(100) NOT NULL,
                    referencia VARCHAR(200),
                    modelo_maquina VARCHAR(100) NOT NULL,
                    equipamento VARCHAR(100) NOT NULL,
                    preco DECIMAL(10, 2) NOT NULL,
                    forma_aluguel VARCHAR(5) NOT NULL,
                    imagem_url VARCHAR(200),
                    descricao TEXT,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """) 

            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS imagens_maquinas (
                    id SERIAL PRIMARY KEY,
                    maquina_id INTEGER NOT NULL REFERENCES maquinas(id) ON DELETE CASCADE,
                    imagem_url VARCHAR(200) NOT NULL
                )
                """)   
            
            self.connection.commit()
            cursor.close()
            print(" Tabelas criadas!")
            return True
        except Exception as e:
            print(f" Erro ao criar tabela: {e}")
            return False
    
    def hash_senha(self, senha):
        """Cria hash da senha"""
        return hashlib.sha256(senha.encode()).hexdigest()
    
    def cadastrar_usuario(self, nome, telefone, cpf, email, senha):
        """Cadastra um usuário"""
        try:
            cursor = self.connection.cursor()
            
            # Verificar se email já existe
            cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
            if cursor.fetchone():
                return "Email já cadastrado"
            
            # Verificar se CPF já existe
            cursor.execute("SELECT id FROM usuarios WHERE cpf = %s", (cpf,))
            if cursor.fetchone():
                return "CPF já cadastrado"
            
            # Inserir usuário
            senha_hash = self.hash_senha(senha)
            cursor.execute("""
                INSERT INTO usuarios (nome, telefone, cpf, email, senha)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (nome, telefone, cpf, email, senha_hash))
            
            user_id = cursor.fetchone()[0]
            self.connection.commit()
            cursor.close()
            
            print(f" Usuário cadastrado! ID: {user_id}")
            return "Sucesso"
            
        except Exception as e:
            print(f" Erro: {e}")
            return "Erro interno"
    
    def listar_usuarios(self):
        """Lista todos os usuários"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id, nome, email, cpf, telefone FROM usuarios ORDER BY id")
            usuarios = cursor.fetchall()
            cursor.close()
            
            # Converter para lista de dicionários
            lista_usuarios = []
            for usuario in usuarios:
                lista_usuarios.append({
                    'id': usuario[0],
                    'nome': usuario[1],
                    'email': usuario[2],
                    'cpf': usuario[3],
                    'telefone': usuario[4]
                })
            
            return lista_usuarios
        except Exception as e:
            print(f" Erro ao listar: {e}")
            return []

    
    def login_email(self, email):
        """Busca um usuário pelo email"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, nome, senha FROM usuarios WHERE email = %s", (email,))
        resultado = cursor.fetchone()
        if resultado:
            return {'id': resultado[0], 'nome': resultado[1], 'senha': resultado[2]}
        return None
    
    def fechar(self):
        """Fecha a conexão"""
        if self.connection:
            self.connection.close()
            print(" Conexão fechada")


################### CADASTRAR MAQUINAS ###############

    def cadastrar_maquina(self, cep, uf, numero, cidade, rua, referencia, 
                         modelo_maquina, equipamento, preco, forma_aluguel, 
                            descricao=None):
        """Cadastra uma máquina com todos os campos"""
        
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO maquinas (cep, uf, numero, cidade, rua, referencia,
                                    modelo_maquina, equipamento, preco, forma_aluguel,
                                    descricao)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (cep, uf, numero, cidade, rua, referencia, modelo_maquina, 
                 equipamento, preco, forma_aluguel, descricao))
            
            maquina_id = cursor.fetchone()[0]
            self.connection.commit()
            cursor.close()
            
            print(f" Máquina cadastrada! ID: {maquina_id}")
            return maquina_id
        except Exception as e:
            print(f" Erro ao cadastrar máquina: {e}")
            return "Erro interno"
    
    def listar_maquinas(self):
        """Lista todas as máquinas com todos os campos"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, cep, uf, numero, cidade, rua, referencia, 
                       modelo_maquina, equipamento, preco, forma_aluguel, 
                       descricao 
                FROM maquinas ORDER BY id
            """)
            maquinas = cursor.fetchall()
            cursor.close()
            
            lista_maquinas = []
            for maquina in maquinas:
                lista_maquinas.append({
                    'id': maquina[0],
                    'cep': maquina[1],
                    'uf': maquina[2],
                    'numero': maquina[3],
                    'cidade': maquina[4],
                    'rua': maquina[5],
                    'referencia': maquina[6],
                    'modelo_maquina': maquina[7],
                    'equipamento': maquina[8],
                    'preco': maquina[9],
                    'forma_aluguel': maquina[10],
                    'descricao': maquina[11]
                })
            return lista_maquinas
        except Exception as e:
            print(f" Erro ao listar máquinas: {e}")
            return []
        
    def cadastrar_imagens_maquina(self, maquina_id, imagens_urls):
        try:
            cursor = self.connection.cursor()
            for url in imagens_urls:
                cursor.execute("""
                    INSERT INTO imagens_maquinas (maquina_id, imagem_url)
                    VALUES (%s, %s)
                """, (maquina_id, url))
            self.connection.commit()
            cursor.close()
            print(f"Imagens cadastradas para a máquina {maquina_id}")
            return True
        except Exception as e:
            print(f"Erro cadastrar_imagens_maquina: {e}")
            return False
    
# Instância global
banco = banco()

def inicializar_banco():
    """Inicializa o banco de dados"""
    if not banco.criar_banco():
        return False
    
    if not banco.conectar():
        return False
    
    if not banco.criar_tabela():
        return False
    
    return True

