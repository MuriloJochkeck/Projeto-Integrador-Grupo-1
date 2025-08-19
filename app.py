from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from banco import banco, inicializar_banco

app = Flask(__name__)
app.secret_key = 'dev-secret-change-me'

# Inicializar banco
inicializar_banco()

# Rotas básicas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro') 
def cadastro():
    return render_template('pages/cadastro_usuario.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET' and session.get('usuario'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        usuario = (request.form.get('usuario') or '').strip()
        senha = (request.form.get('senha') or '').strip()

        if not usuario or not senha:
            return render_template('pages/login_usuario.html', error='Preencha email/telefone e senha.')

        import re
        eh_email = re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', usuario) is not None
        somente_digitos = re.sub(r'\D', '', usuario)
        eh_telefone = re.match(r'^\d{10,11}$', somente_digitos) is not None

        if not (eh_email or eh_telefone):
            return render_template('pages/login_usuario.html', error='Informe um email ou telefone válido.')

        if len(senha) < 6:
            return render_template('pages/login_usuario.html', error='Senha deve ter ao menos 6 caracteres.')

        usuario_bd = banco.autenticar_usuario(usuario, senha)
        if not usuario_bd:
            return render_template('pages/login_usuario.html', error='Credenciais inválidas.')

        session['usuario'] = usuario_bd
        return redirect(url_for('index'))

    return render_template('pages/login_usuario.html')

@app.route('/carrinho') 
def carrinho():
    return render_template('pages/carrinho.html')

@app.route('/aluguel')
def aluguel():
    return render_template('pages/aluguel.html')

@app.route('/endereço_user')
def endereço_user():
    return render_template('pages/endereco_usuario.html')

@app.route('/cadastro_maquinas')
def cadastro_maquinas():
    return render_template('pages/cadastro_maquinas.html')

@app.route('/cadastro_maquinas2')
def cadastro_maquinas2():
    return render_template('pages/cadastro_maquinas2.html')

@app.route('/finaliza_pedido')
def finaliza_pedido():
    return render_template('pages/finaliza_pedido.html')

# Cadastro de usuário
@app.route('/api/cadastro', methods=['POST'])
def db_cadastro():
    try:
        dados = request.get_json(silent=True) or {}
        
        # Validar campos obrigatórios
        campos_obrigatorios = ['nome_user', 'telefone_user', 'cpf', 'email', 'senha']
        for campo in campos_obrigatorios:
            if not dados.get(campo):
                return jsonify({'success': False, 'message': f'Campo {campo} é obrigatório'}), 400
        
        # Cadastrar usuário usando o banco PostgreSQL
        resultado = banco.cadastrar_usuario(
            nome=dados['nome_user'],
            telefone=dados['telefone_user'],
            cpf=dados['cpf'],
            email=dados['email'],
            senha=dados['senha']
        )
        
        if resultado == "Sucesso":
            return jsonify({
                'success': True, 
                'message': 'Usuário cadastrado com sucesso!'
            }), 201
        else:
            return jsonify({'success': False, 'message': resultado}), 400
        
    except Exception as e:
        print(f"Erro ao cadastrar usuário: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

# Listar usuários
@app.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    try:
        usuarios = banco.listar_usuarios()
        return jsonify({
            'success': True,
            'usuarios': usuarios,
            'total': len(usuarios)
        })
    except Exception as e:
        print(f"Erro ao listar usuários: {str(e)}")
        return jsonify({'success': False, 'message': 'Erro ao listar usuários'}), 500

if __name__ == '__main__':
    app.run(debug=True)