from flask import Flask, render_template, request, jsonify
from banco import banco, inicializar_banco

app = Flask(__name__)

# Inicializar banco
inicializar_banco()

# Rotas básicas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastro') 
def cadastro():
    return render_template('pages/cadastro_usuario.html')

@app.route('/login')
def login():
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
@app.route('/api/cadastro', methods=['GET', 'POST'])
def db_cadastro():
    try:
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