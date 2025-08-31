from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from banco import banco, inicializar_banco
from functools import wraps
from supabase import create_client, Client
from acessodb import supabase_url, supabase_key, bucket_name

SUPABASE_URL = supabase_url
SUPABASE_KEY = supabase_key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = 'PI@2025'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def imagem_permitida(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Inicializar banco
inicializar_banco()

# Rotas básicas
@app.route('/')
def index():
    maquinas = banco.listar_maquinas()
    return render_template('index.html', maquinas=maquinas)

@app.route('/cadastro') 
def cadastro():
    return render_template('pages/cadastro_usuario.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        try:
            # Tenta fazer login com Supabase Auth
            user_session = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            
            if user_session.user:
                # Busca os dados adicionais do usuário na sua tabela 'usuarios'
                user_data = banco.get_user_by_id(user_session.user.id)
                if user_data:
                    session['usuario_id'] = user_session.user.id
                    session['usuario_nome'] = user_data['nome'] # Assume que 'nome' está na sua tabela 'usuarios'
                    return redirect(url_for('index'))
                else:
                    # Usuário autenticado no Supabase Auth, mas não encontrado na sua tabela 'usuarios'
                    # Isso pode indicar um problema na criação inicial do usuário ou na sincronização
                    supabase.auth.sign_out() # Desloga para evitar inconsistência
                    mensagem = 'Erro ao carregar dados do usuário. Tente novamente.'
                    return render_template('pages/login_usuario.html', mensagem=mensagem)
            else:
                mensagem = 'Email ou senha incorretos.'
                return render_template('pages/login_usuario.html', mensagem=mensagem)
        except Exception as e:
            print(f"Erro de login: {e}")
            mensagem = 'Email ou senha incorretos.' # Mensagem genérica por segurança
            return render_template('pages/login_usuario.html', mensagem=mensagem)

    return render_template('pages/login_usuario.html')
        


@app.route('/carrinho') 
@login_required
def carrinho():
    return render_template('pages/carrinho.html')

@app.route('/aluguel')
def aluguel():
    maquinas = banco.listar_maquinas()
    return render_template('pages/aluguel.html' , maquinas=maquinas)

@app.route('/maquina/<int:maquina_id>')
def ver_maquina(maquina_id):
    maquinas = banco.listar_maquinas()
    maquina = next((m for m in maquinas if m['id'] == maquina_id), None)
    if not maquina:
        return "Máquina não encontrada", 404
    return render_template('pages/aluguel.html', maquina=maquina)


@app.route('/endereço_user')
def endereço_user():
    return render_template('pages/endereco_usuario.html')

@app.route('/cadastro_maquinas')
def cadastro_maquinas():
    return render_template('pages/cadastro_maquinas.html')

@app.route('/ver_mais_colheitadeira')
def ver_mais_colheitadeira():
    return render_template('pages/ver_mais_colheitadeira.html')

@app.route('/ver_mais_trator')
def ver_mais_trator():
    return render_template('pages/ver_mais_trator.html')

@app.route('/finaliza_pedido')
@login_required
def finaliza_pedido():
    usuario_id = session['usuario_id']
    carrinho = banco.listar_itens_carrinho(usuario_id)
    total = sum(item['preco'] * item['quantidade'] for item in carrinho)
    return render_template('pages/finaliza_pedido.html', total=total)

    


@app.route('/sobrenos')
def sobrenos():
    return render_template('pages/sobrenos.html')

@app.route('/faleconosco')
def faleconosco():
    return render_template('pages/faleconosco.html')


################# USUÁRIOS #######################

@app.route('/api/cadastro', methods=['GET', 'POST'])
def db_cadastro():
    nome = request.form.get('nome_user')
    telefone = request.form.get('telefone_user')
    cpf = request.form.get('cpf')
    email = request.form.get('email')
    senha = request.form.get('senha')

    if not all([nome, telefone, cpf, email, senha]):
        return jsonify({"success": False, "message": "Todos os campos são obrigatórios"}), 400

    try:
        existing = supabase.table("usuarios").select("*").eq("email", email).execute()
        if existing.data:
            return jsonify({"success": False, "message": "Email já cadastrado"}), 400

        # Cria o usuário no Auth
        usuario = supabase.auth.admin.create_user({
            'email': email,
            'password': senha,
            'email_confirm': True,
            'user_metadata': {'nome': nome}  
        })


        supabase_uid = usuario.user.id
        # Agora insere no banco local
        resultado = banco.cadastrar_usuario(nome, telefone, cpf, email, supabase_uid)

        if resultado == "Sucesso":
            return redirect(url_for('index'))
        else:
            return jsonify({"success": False, "message": "Erro ao salvar no banco local"}), 500

    except Exception as e:
        print("Erro ao cadastrar usuário:", e)
        import traceback
        traceback.print_exc()
        return redirect(url_for('index'))

@app.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
        usuarios = banco.listar_usuarios()
        return jsonify({
            'success': True,
            'usuarios': usuarios,
            'total': len(usuarios)
        })

################# MAQUINAS #######################

@app.route('/api/cadastro_maquinas', methods=['GET', 'POST'])
@login_required
def cadastrar_maquinas():
    usuario_id = session.get('usuario_id') # Pega o ID do usuário logado
    if not usuario_id:
        return jsonify({"success": False, "message": "Usuário não logado"}), 401

    try:
        # Primeiro cadastra a máquina
        maquina_id = banco.cadastrar_maquina(
            cep=request.form["cep"],
            uf=request.form["uf"],
            numero=request.form["numero"],
            cidade=request.form["cidade"],
            rua=request.form["rua"],
            referencia=request.form.get("referencia"),
            modelo_maquina=request.form["modelo"],
            equipamento=request.form["equipamento"],
            preco = request.form["preco"].replace("R$", "").replace(".", "").replace(",", ".").strip(),
            forma_aluguel=request.form.get("forma_aluguel"),
            descricao=request.form.get("descricao"),
            usuario_id=usuario_id # Passa o ID do usuário logado
        )

        if maquina_id is None:
            raise Exception("Falha ao cadastrar máquina no banco de dados.")

        imagens = request.files.getlist("imagens")
        uploaded_image_urls = []
        for img in imagens:
            if img and img.filename != "":
                if not imagem_permitida(img.filename):
                    print(f"Arquivo não permitido: {img.filename}")
                    continue
                
                # Upload para o Supabase Storage
                file_path = f"{maquina_id}/{img.filename}" # Ex: "123/imagem.jpg"
                try:
                    response = supabase.storage.from_(bucket_name).upload(file_path, img.read())
                    if response.status_code == 200: # Verifica se o upload foi bem-sucedido
                        public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
                        uploaded_image_urls.append(public_url)
                    else:
                        print(f"Erro no upload para Supabase: {response.json()}")
                except Exception as storage_e:
                    print(f"Exceção durante o upload para Supabase: {storage_e}")
                    continue
        
        # Salva as URLs das imagens no banco de dados
        if uploaded_image_urls:
            banco.cadastrar_imagens_maquina(maquina_id, uploaded_image_urls)

        return redirect(url_for('index'))

    except Exception as e:
        print("Erro ao cadastrar máquina:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"Erro ao cadastrar máquina: {str(e)}"}), 500
        
    
@app.route('/api/maquinas', methods=['GET'])
def list_maquinas():
    maquinas = banco.listar_maquinas()
    return jsonify({
        'success': True,
        'maquinas': maquinas,
        'total': len(maquinas)
    })


####################### CARRINHO #########################



if __name__ == '__main__':
    app.run(debug=True)