from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from banco import banco, inicializar_banco
import hashlib
from functools import wraps
from supabase import create_client, Client
from acessodb import supabase_url, supabase_key, bucket_name

SUPABASE_URL = supabase_url
SUPABASE_KEY = supabase_key
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
app.secret_key = 'PI2025GRUPO1'  

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

        senha_hash = hashlib.sha256(senha.encode()).hexdigest()

        # Busca usuário no banco
        usuario = banco.login_email(email)  

        if usuario and usuario['senha'] == senha_hash:
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['nome']
            return redirect(url_for('index'))
        else:
            mensagem = 'Email ou senha incorretos'
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

        # Salva os dados extras na tabela "usuarios"
        supabase.table('usuarios').insert({
            'id': usuario.user.id,  # id do Auth
            'nome': nome,
            'telefone': telefone,
            'cpf': cpf
        }).execute()

        return redirect(url_for('index'))

    except Exception as e:
        print("Erro ao cadastrar usuário:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500

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
             
        )

        imagens = request.files.getlist("imagens")
        id_maquina = maquina_id  
        for img in imagens:
            if img and img.filename != "":
                if not imagem_permitida(img.filename):
                    continue
                
                banco.cadastrar_imagens_maquina(id_maquina, [img])

        return redirect(url_for('index'))

    except Exception as e:
        print("Erro ao cadastrar máquina:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": "Erro ao cadastrar máquina"}), 500
    
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