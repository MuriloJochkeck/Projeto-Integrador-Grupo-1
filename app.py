from flask import Flask, render_template   


app = Flask(__name__)


# %%%%%%%%%%%%%%%%%%% ROTAS %%%%%%%%%%%%%%%%%%%%%


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('pages/login_usuario.html')

@app.route('/carrinho') 
def carrinho():
    return render_template('pages/carrinho.html')

@app.route('/cadastro') 
def cadastro():
    return render_template('pages/cadastro_usuario.html')

@app.route('/aluguel')
def aluguel():
    return render_template('pages/aluguel.html')

@app.route('/endereço_user')
def endereço_user():
    return render_template('pages/endereço_usuario.html')


# %%%%%%%%%%%%%%%%%%% ROTAS CADASTRO DE MAQUINAS %%%%%%%%%%%%%%%%%%%%%

@app.route('/cadastro_maquinas')
def cadastro_maquinas():
    return render_template('pages/cadastro_maquinas.html')

@app.route('/cadastro_maquinas2')
def cadastro_maquinas2():
    return render_template('pages/cadastro_maquinas2.html')




if __name__ == '__main__':
    app.run(debug=True)