import psycopg2
import hashlib
from acessodb import db_host, db_port, db_user, db_password, db_database, supabase_url, supabase_key, bucket_name
from supabase import create_client, Client

SUPABASE_URL = supabase_url
SUPABASE_KEY = supabase_key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
BUCKET_NAME = bucket_name

class Banco:
    def __init__(self):
        self.host = db_host
        self.port = db_port
        self.database = db_database
        self.user = db_user
        self.password = db_password
        self.connection = None

    def conectar(self):
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print("Conectado!")
            return True
        except Exception as e:
            print(f"Erro ao conectar: {e}")
            return False

    def criar_tabela(self):
        "Criar tabelas"
        try:
            cursor = self.connection.cursor()
            
            # Usuários
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
                    nome VARCHAR(100) NOT NULL,
                    telefone VARCHAR(20) NOT NULL,
                    cpf VARCHAR(14) UNIQUE NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    senha VARCHAR(200) NOT NULL,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Máquinas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS maquinas (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                    cep VARCHAR(10) NOT NULL,
                    uf CHAR(2) NOT NULL,
                    numero INTEGER NOT NULL,
                    cidade VARCHAR(50) NOT NULL,
                    rua VARCHAR(100) NOT NULL,
                    referencia VARCHAR(200),
                    modelo_maquina VARCHAR(150) NOT NULL,
                    equipamento VARCHAR(150) NOT NULL,
                    preco DECIMAL(10,2) NOT NULL,
                    forma_aluguel VARCHAR(5) NOT NULL,
                    descricao TEXT,
                    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Imagens das máquinas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS imagens_maquinas (
                    id SERIAL PRIMARY KEY,
                    maquina_id INTEGER NOT NULL REFERENCES maquinas(id) ON DELETE CASCADE,
                    imagem_url VARCHAR(200) NOT NULL
                )
            """)
            
            # Carrinhos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS carrinhos (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE (usuario_id)
                )
            """)
            
            # Itens do carrinho
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS itens_carrinho (
                    id SERIAL PRIMARY KEY,
                    carrinho_id INTEGER NOT NULL REFERENCES carrinhos(id) ON DELETE CASCADE,
                    maquina_id INTEGER NOT NULL REFERENCES maquinas(id) ON DELETE CASCADE,
                    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
                    forma_aluguel VARCHAR(5) NOT NULL,
                    UNIQUE (carrinho_id, maquina_id)
                )
            """)
            
            self.connection.commit()
            cursor.close()
            print("Tabelas criadas/verificadas!")
            return True
        except Exception as e:
            self.connection.rollback()
            print(f"Erro ao criar tabela: {e}")
            return False

    # ----------------- Usuários -----------------

    def hash_senha(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()

    def listar_usuarios(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id, nome, email, cpf, telefone FROM usuarios ORDER BY id")
            usuarios = cursor.fetchall()
            cursor.close()
            return [{'id': u[0], 'nome': u[1], 'email': u[2], 'cpf': u[3], 'telefone': u[4]} for u in usuarios]
        except Exception as e:
            print(f"Erro listar_usuarios: {e}")
            return []

    def login_email(self, email):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id, nome, senha FROM usuarios WHERE email=%s", (email,))
            resultado = cursor.fetchone()
            cursor.close()
            if resultado:
                return {'id': resultado[0], 'nome': resultado[1], 'senha': resultado[2]}
            return None
        except Exception as e:
            print(f"Erro login_email: {e}")
            return None

    # ----------------- Máquinas -----------------

    def cadastrar_maquina(self, cep, uf, numero, cidade, rua, referencia,
                          modelo_maquina, equipamento, preco, forma_aluguel, descricao=None, usuario_id=None):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO maquinas (usuario_id, cep, uf, numero, cidade, rua, referencia,
                                      modelo_maquina, equipamento, preco, forma_aluguel, descricao)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id
            """, (usuario_id, cep, uf, numero, cidade, rua, referencia,
                  modelo_maquina, equipamento, preco, forma_aluguel, descricao))
            maquina_id = cursor.fetchone()[0]
            self.connection.commit()
            cursor.close()
            print(f"Máquina cadastrada! ID: {maquina_id}")
            return maquina_id
        except Exception as e:
            print(f"Erro cadastrar_maquina: {e}")
            return None

    def cadastrar_imagens_maquina(self, maquina_id, imagens_urls):
        try:
            cursor = self.connection.cursor()
            
            # Se veio apenas um arquivo, transforma em lista
            if not isinstance(imagens_urls, list):
                imagens_urls = [imagens_urls]

            for arquivo in imagens_urls:
                # arquivo.filename já existe sem precisar abrir local
                nome_arquivo = arquivo.filename
                conteudo = arquivo.read()

                # Envia direto para o bucket do Supabase
                supabase.storage.from_(BUCKET_NAME).upload(
                    path=nome_arquivo,  # caminho dentro do bucket
                    file=conteudo       # bytes do arquivo
                )

                # Aqui você pode salvar a URL retornada no banco
                url_arquivo = supabase.storage.from_(BUCKET_NAME).get_public_url(nome_arquivo)
                cursor.execute(
                    "INSERT INTO imagens_maquina (maquina_id, url) VALUES (%s, %s)",
                    (maquina_id, url_arquivo)
                )
            
            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print("Erro cadastrar_imagens_maquina:", e)
            return False
                

    def listar_maquinas(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT m.id, m.modelo_maquina, m.equipamento, m.preco, m.forma_aluguel,
                       m.descricao, u.nome AS usuario_nome,
                       COALESCE(array_agg(i.imagem_url) FILTER (WHERE i.imagem_url IS NOT NULL), '{}') AS imagens
                FROM maquinas m
                LEFT JOIN usuarios u ON m.usuario_id = u.id
                LEFT JOIN imagens_maquinas i ON m.id = i.maquina_id
                GROUP BY m.id, m.modelo_maquina, m.equipamento, m.preco, m.forma_aluguel, m.descricao, u.nome
                ORDER BY m.id
            """)
            maquinas = cursor.fetchall()
            cursor.close()
            return [{
                'id': m[0],
                'modelo_maquina': m[1],
                'equipamento': m[2],
                'preco': float(m[3]),
                'forma_aluguel': m[4],
                'descricao': m[5],
                'usuario_nome': m[6] if m[6] else "Desconhecido",
                'imagens': m[7]
            } for m in maquinas]
        except Exception as e:
            print(f"Erro listar_maquinas: {e}")
            return []

    # ----------------- Conexão -----------------

    def fechar(self):
        if self.connection:
            self.connection.close()
            print("Conexão fechada")

# ----------------- Instância global -----------------

banco = Banco()

def inicializar_banco():
    """Inicializa banco no Supabase"""
    if not banco.conectar():
        return False
    if not banco.criar_tabela():
        return False
    return True

