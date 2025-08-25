from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from banco import banco, inicializar_banco
import hashlib
import os
from werkzeug.utils import secure_filename
from functools import wraps

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
    return render_template('index.html', maquinas = maquinas)

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
def carrinho():
    return render_template('pages/carrinho.html')

@app.route('/aluguel')
def aluguel():
    maquinas = banco.listar_maquinas()
    return render_template('pages/aluguel.html' , maquinas=maquinas)

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

    


# Cadastro de usuário
@app.route('/api/cadastro', methods=['GET', 'POST'])
def db_cadastro():
        if request.method == 'POST':        
            # Cadastrar usuário usando o banco PostgreSQL
            resultado = banco.cadastrar_usuario(
                nome = request.form['nome_user'],
                telefone = request.form['telefone_user'],
                cpf = request.form['cpf'],
                email = request.form['email'],
                senha = request.form['senha']
            )

        if resultado == "Sucesso":
            return redirect(url_for('index'))
        else:
            return jsonify({'success': False, 'message': resultado}), 400


@app.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
        usuarios = banco.listar_usuarios()
        return jsonify({
            'success': True,
            'usuarios': usuarios,
            'total': len(usuarios)
        })

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
                filename = secure_filename(img.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                imagem_url = f"uploads/{filename}"  # Caminho relativo à pasta 'static'
                img.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                # Salvar no banco apenas 'uploads/nome_da_imagem.ext'
                banco.cadastrar_imagens_maquina(id_maquina, [imagem_url])

        return redirect(url_for('index'))

    except Exception as e:
        print("Erro ao cadastrar máquina:", e)
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": "Erro ao cadastrar máquina"}), 500
    
def cadastrar_imagens_maquina(self, maquina_id, imagens):
    """Cadastra várias imagens de uma máquina"""
    try:
        cursor = self.connection.cursor()
        for img in imagens:
            cursor.execute("""
                INSERT INTO imagens_maquinas (maquina_id, imagem_url)
                VALUES (%s, %s)
            """, (maquina_id, img))
        self.connection.commit()
        cursor.close()
        return "Sucesso"
    except Exception as e:
        print(f"Erro ao cadastrar imagens: {e}")
        return "Erro interno"

def listar_maquinas(self):
    try:
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT m.id, m.modelo_maquina, m.equipamento, m.preco, m.forma_aluguel,
                   COALESCE(
                       (SELECT imagem_url FROM imagens_maquinas WHERE maquina_id = m.id LIMIT 1), 
                       ''
                   ) as imagem_url
            FROM maquinas m ORDER BY m.id
        """)
        maquinas = cursor.fetchall()
        cursor.close()

        lista_maquinas = []
        for m in maquinas:
            # Corrige barras e remove "static/" caso esteja duplicado
            imagens = m[5].replace("\\", "/") if m[5] else ""
            lista_maquinas.append({
                'id': m[0],
                'modelo_maquina': m[1],
                'equipamento': m[2],
                'preco': float(m[3]),
                'forma_aluguel': m[4],
                'imagem_url': imagens
            })
        return lista_maquinas
    except Exception as e:
        print(f"Erro listar_maquinas: {e}")
        return []
    
@app.route('/api/maquinas', methods=['GET'])
def list_maquinas():
    maquinas = banco.listar_maquinas()
    return jsonify({
        'success': True,
        'maquinas': maquinas,
        'total': len(maquinas)
    })


if __name__ == '__main__':
    app.run(debug=True)