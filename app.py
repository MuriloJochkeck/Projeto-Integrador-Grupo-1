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
    return render_template('pages/cadastro.html')


# %%%%%%%%%%%%%%%%%%% ROTAS CADASTRO DE MAQUINAS %%%%%%%%%%%%%%%%%%%%%

@app.route('/cadastro_maquinas')
def cadastro_maquinas():
    return render_template('pages/cadastro_maquinas.html')





if __name__ == '__main__':
    app.run(debug=True)