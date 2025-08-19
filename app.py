from flask import Flask, render_template, request, redirect, url_for, session  

app = Flask(__name__)
app.secret_key = 'dev-secret-change-me'



# %%%%%%%%%%%%%%%%%%% ROTAS %%%%%%%%%%%%%%%%%%%%%


@app.route('/')
def index():
    return render_template('index.html')

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

        # Exemplo de autenticação fake: aceita qualquer combinação válida de formato
        session['usuario'] = usuario
        return redirect(url_for('index'))

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