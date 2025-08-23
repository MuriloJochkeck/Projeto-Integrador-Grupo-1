from flask import Flask, render_template, request, jsonify, redirect, url_for
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


@app.route('/finaliza_pedido')
def finaliza_pedido():
    return render_template('pages/finaliza_pedido.html', total=0)



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

# @app.route('/api/cadastro_maquinas', methods=['GET', 'POST'])
# def cadastrar_maquinas():
#     if request.method == 'POST':
#         # Cadastrar máquina usando o banco PostgreSQL
#         resultado = banco.cadastrar_maquina(
#             cep = request.form['cep'],
#             uf = request.form['uf'],
#             numero = request.form['numero'],
#             cidade = request.form['cidade'],
#             rua = request.form['rua'],
#             referencia = request.form['referencia']
#         )

#         if resultado == "Sucesso":
#             return redirect(url_for('index'))
#         else:
#             return jsonify({'success': False, 'message': resultado}), 400

@app.route('/api/maquinas', methods=['GET'])
def listar_maquinas():
    maquinas = banco.listar_maquinas()
    return jsonify({
        'success': True,
        'maquinas': maquinas,
        'total': len(maquinas)
    })


if __name__ == '__main__':
    app.run(debug=True)