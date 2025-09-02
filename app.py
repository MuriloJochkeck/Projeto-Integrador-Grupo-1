from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from banco import banco, inicializar_banco
from functools import wraps
from supabase import create_client, Client
from acessodb import supabase_url, supabase_key, bucket_name
import base64

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
    user = banco.listar_usuarios()
    return render_template('index.html', maquinas=maquinas, user=user)

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
            
            # if user_session.user:
            #     # Busca os dados adicionais do usuário na sua tabela 'usuarios'
            #     user_data = banco.get_user_by_id(user_session.user.id)
            #     if user_data:
            #         session['usuario_id'] = user_session.user.id
            #         session['usuario_nome'] = user_data['nome'] # Assume que 'nome' está na sua tabela 'usuarios'
            #         return redirect(url_for('index'))
            #     else:
            #         # Usuário autenticado no Supabase Auth, mas não encontrado na sua tabela 'usuarios'
            #         # Isso pode indicar um problema na criação inicial do usuário ou na sincronização
            #         supabase.auth.sign_out() # Desloga para evitar inconsistência
            #         mensagem = 'Erro ao carregar dados do usuário. Tente novamente.'
            #         return render_template('pages/login_usuario.html', mensagem=mensagem)
            # else:
            #     mensagem = 'Email ou senha incorretos.'
            #     return render_template('pages/login_usuario.html', mensagem=mensagem)
            if user_session.user:
                user_data = banco.get_user_by_id(user_session.user.id)
                if user_data:
                    session['usuario_id'] = user_session.user.id
                    session['usuario_nome'] = user_data['nome']
                    return redirect(url_for('index'))
                else:
                    supabase.auth.sign_out()
                    mensagem = 'Erro ao carregar dados do usuário. Tente novamente.'
                    return render_template('pages/login_usuario.html', mensagem=mensagem)

        except Exception as e:
            print(f"Erro de login: {e}")
            mensagem = 'Email ou senha incorretos.' # Mensagem genérica por segurança
            return render_template('pages/login_usuario.html', mensagem=mensagem)

    return render_template('pages/login_usuario.html')
        


@app.route('/carrinho') 
@login_required
def carrinho():
    usuario_id = session['usuario_id']
    itens = banco.listar_itens_carrinho(usuario_id)
    total = sum(item['subtotal'] for item in itens)
    return render_template('pages/carrinho.html', itens=itens, total=total)

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
        resultado = supabase.table("usuarios").insert({
            "id": supabase_uid,
            "nome": nome,
            "telefone": telefone,
            "cpf": cpf,
            "email": email
        }).execute()


        if resultado.data == "Sucesso":
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))

    except Exception as e:
        print("Erro ao cadastrar usuário:", e)
        import traceback
        traceback.print_exc()
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    # Remove dados do Flask session
    session.pop('usuario_id', None)
    session.pop('usuario_nome', None)

    # Opcional: desloga do Supabase Auth
    try:
        supabase.auth.sign_out()
    except Exception as e:
        print(f"Erro ao deslogar do Supabase: {e}")

    # Redireciona para a página de login ou index
    return redirect(url_for('login'))

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



@app.route('/api/carrinho/adicionar', methods=['POST'])
@login_required
def adicionar_ao_carrinho():
    """Adiciona uma máquina ao carrinho"""
    try:
        usuario_id = session['usuario_id']
        maquina_id = request.form.get('maquina_id')
        quantidade = int(request.form.get('quantidade', 1))
        forma_aluguel = request.form.get('forma_aluguel', 'DIA')
        
        if not maquina_id:
            return jsonify({"success": False, "message": "ID da máquina é obrigatório"}), 400
        
        if quantidade <= 0:
            return jsonify({"success": False, "message": "Quantidade deve ser maior que zero"}), 400
        
        # Verifica se a máquina existe
        maquina = banco.obter_maquina_por_id(maquina_id)
        if not maquina:
            return jsonify({"success": False, "message": "Máquina não encontrada"}), 404
        
        # Adiciona ao carrinho
        sucesso = banco.adicionar_ao_carrinho(usuario_id, maquina_id, quantidade, forma_aluguel)
        
        if sucesso:
            return jsonify({
                "success": True, 
                "message": "Máquina adicionada ao carrinho com sucesso!",
                "maquina": maquina
            })
        else:
            return jsonify({"success": False, "message": "Erro ao adicionar ao carrinho"}), 500
            
    except Exception as e:
        print(f"Erro ao adicionar ao carrinho: {e}")
        return jsonify({"success": False, "message": "Erro interno do servidor"}), 500

@app.route('/carrinho/adicionar', methods=['POST'])
@login_required
def carrinho_adicionar():
    """Adiciona ou atualiza um item no carrinho (versão para formulário HTML)"""
    try:
        usuario_id = session['usuario_id']
        maquina_id = request.form.get('maquina_id')
        forma_aluguel = request.form.get('forma_aluguel', 'DIA')
        acao = request.form.get('acao')
        
        # Obtém o item atual do carrinho para saber a quantidade
        itens = banco.listar_itens_carrinho(usuario_id)
        item_atual = next((item for item in itens if str(item['id']) == str(maquina_id)), None)
        
        if acao == 'increment':
            # Incrementa a quantidade
            if item_atual:
                nova_quantidade = item_atual['quantidade'] + 1
                banco.atualizar_quantidade_carrinho(usuario_id, maquina_id, nova_quantidade)
            else:
                # Se não existe, adiciona com quantidade 1
                banco.adicionar_ao_carrinho(usuario_id, maquina_id, 1, forma_aluguel)
        elif acao == 'decrement':
            # Decrementa a quantidade
            if item_atual and item_atual['quantidade'] > 1:
                nova_quantidade = item_atual['quantidade'] - 1
                banco.atualizar_quantidade_carrinho(usuario_id, maquina_id, nova_quantidade)
            elif item_atual:
                # Se a quantidade é 1, remove o item
                banco.remover_do_carrinho(usuario_id, maquina_id)
        
        # Redireciona de volta para a página do carrinho
        return redirect(url_for('carrinho'))
        
    except Exception as e:
        print(f"Erro ao atualizar carrinho: {e}")
        flash("Erro ao atualizar carrinho", "error")
        return redirect(url_for('carrinho'))

@app.route('/api/carrinho/remover', methods=['POST'])
@login_required
def remover_do_carrinho():
    """Remove uma máquina do carrinho (API)"""
    try:
        usuario_id = session['usuario_id']
        maquina_id = request.form.get('maquina_id')
        
        if not maquina_id:
            return jsonify({"success": False, "message": "ID da máquina é obrigatório"}), 400
        
        sucesso = banco.remover_do_carrinho(usuario_id, maquina_id)
        
        if sucesso:
            return jsonify({"success": True, "message": "Máquina removida do carrinho com sucesso!"})
        else:
            return jsonify({"success": False, "message": "Erro ao remover do carrinho"}), 500
            
    except Exception as e:
        print(f"Erro ao remover do carrinho: {e}")
        return jsonify({"success": False, "message": "Erro interno do servidor"}), 500

@app.route('/carrinho/remover/<int:item_id>', methods=['GET'])
@login_required
def carrinho_remover(item_id):
    """Remove um item do carrinho (versão para link HTML)"""
    try:
        usuario_id = session['usuario_id']
        sucesso = banco.remover_do_carrinho(usuario_id, item_id)
        
        if not sucesso:
            flash("Erro ao remover item do carrinho", "error")
            
        return redirect(url_for('carrinho'))
        
    except Exception as e:
        print(f"Erro ao remover do carrinho: {e}")
        flash("Erro ao remover item do carrinho", "error")
        return redirect(url_for('carrinho'))


@app.route('/salvarImagens', methods=['POST'])
@login_required
def salvar_imagens():
    try:
        if not request.is_json:
            return jsonify({"success": False, "message": "Requisição deve ser JSON"}), 400

        data = request.get_json(silent=True) or {}
        maquina_id = data.get('maquina_id')
        imagens = data.get('imagens') or data.get('imagens_base64') or []

        if not maquina_id:
            return jsonify({"success": False, "message": "maquina_id é obrigatório"}), 400
        if not isinstance(imagens, list) or len(imagens) == 0:
            return jsonify({"success": False, "message": "Lista de imagens (base64) é obrigatória"}), 400

        uploaded_image_urls = []
        for idx, img_b64 in enumerate(imagens):
            if not isinstance(img_b64, str) or len(img_b64.strip()) == 0:
                continue

            # Suporta data URL (ex: data:image/png;base64,....) e base64 puro
            mime_type = 'image/jpeg'
            raw_b64 = img_b64
            if ',' in img_b64 and img_b64.lower().startswith('data:'):
                header, raw_b64 = img_b64.split(',', 1)
                # tenta extrair mime
                try:
                    mime_type = header.split(';')[0].split(':')[1]
                except Exception:
                    mime_type = 'image/jpeg'

            # Define extensão pela mime
            ext_map = {
                'image/jpeg': 'jpg',
                'image/jpg': 'jpg',
                'image/png': 'png',
                'image/gif': 'gif',
                'image/webp': 'webp'
            }
            ext = ext_map.get(mime_type.lower(), 'jpg')

            try:
                file_bytes = base64.b64decode(raw_b64)
            except Exception:
                # base64 inválido, ignora
                continue

            file_path = f"{maquina_id}/b64_{idx}.{ext}"
            try:
                resp = supabase.storage.from_(bucket_name).upload(file_path, file_bytes)
                # Supabase retorna 200 para sucesso
                status_ok = getattr(resp, 'status_code', None) == 200 or (isinstance(resp, dict) and resp.get('Key'))
                if status_ok:
                    public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
                    uploaded_image_urls.append(public_url)
                else:
                    # tenta obter erro textual
                    try:
                        err = resp.json()
                        print(f"Erro upload Supabase: {err}")
                    except Exception:
                        print(f"Erro upload Supabase: {resp}")
                    continue
            except Exception as storage_e:
                print(f"Exceção upload Supabase: {storage_e}")
                continue

        if uploaded_image_urls:
            banco.cadastrar_imagens_maquina(maquina_id, uploaded_image_urls)
            return jsonify({
                "success": True,
                "message": "Imagens salvas com sucesso",
                "total_imagens": len(uploaded_image_urls),
                "urls": uploaded_image_urls
            })
        else:
            return jsonify({"success": False, "message": "Nenhuma imagem válida foi processada"}), 400

    except Exception as e:
        print(f"Erro em /salvarImagens: {e}")
        return jsonify({"success": False, "message": "Erro interno do servidor"}), 500
            
    
# Remove the duplicate set of routes at the bottom of the file to avoid overwriting endpoints
# The unique definitions already exist earlier in the file.
# Keeping only the first definitions, removing the duplicated block below:
@app.route('/api/carrinho/atualizar', methods=['POST'])
@login_required
def atualizar_carrinho():
    """Atualiza a quantidade de uma máquina no carrinho"""
    try:
        usuario_id = session['usuario_id']
        maquina_id = request.form.get('maquina_id')
        nova_quantidade = int(request.form.get('quantidade', 1))
        
        if not maquina_id:
            return jsonify({"success": False, "message": "ID da máquina é obrigatório"}), 400
        
        if nova_quantidade < 0:
            return jsonify({"success": False, "message": "Quantidade não pode ser negativa"}), 400
        
        sucesso = banco.atualizar_quantidade_carrinho(usuario_id, maquina_id, nova_quantidade)
        
        if sucesso:
            if nova_quantidade == 0:
                return jsonify({"success": True, "message": "Item removido do carrinho"})
            else:
                return jsonify({"success": True, "message": "Quantidade atualizada com sucesso!"})
        else:
            return jsonify({"success": False, "message": "Erro ao atualizar carrinho"}), 500
            
    except Exception as e:
        print(f"Erro ao atualizar carrinho: {e}")
        return jsonify({"success": False, "message": "Erro interno do servidor"}), 500

@app.route('/api/carrinho/limpar', methods=['POST'])
@login_required
def limpar_carrinho():
    """Limpa todo o carrinho do usuário"""
    try:
        usuario_id = session['usuario_id']
        
        sucesso = banco.limpar_carrinho(usuario_id)
        
        if sucesso:
            return jsonify({"success": True, "message": "Carrinho limpo com sucesso!"})
        else:
            return jsonify({"success": False, "message": "Erro ao limpar carrinho"}), 500
            
    except Exception as e:
        print(f"Erro ao limpar carrinho: {e}")
        return jsonify({"success": False, "message": "Erro interno do servidor"}), 500

@app.route('/api/carrinho/itens', methods=['GET'])
@login_required
def listar_itens_carrinho():
    """Lista todos os itens do carrinho do usuário"""
    try:
        usuario_id = session['usuario_id']
        itens = banco.listar_itens_carrinho(usuario_id)
        
        # Calcula o total do carrinho
        total = sum(item['subtotal'] for item in itens)
        
        return jsonify({
            "success": True,
            "itens": itens,
            "total": total,
            "total_itens": len(itens)
        })
        
    except Exception as e:
        print(f"Erro ao listar itens do carrinho: {e}")
        return jsonify({"success": False, "message": "Erro interno do servidor"}), 500

@app.route('/api/carrinho/contador', methods=['GET'])
@login_required
def contador_carrinho():
    """Retorna apenas o número de itens no carrinho"""
    try:
        usuario_id = session['usuario_id']
        itens = banco.listar_itens_carrinho(usuario_id)
        
        return jsonify({
            "success": True,
            "total_itens": len(itens)
        })
        
    except Exception as e:
        print(f"Erro ao contar itens do carrinho: {e}")
        return jsonify({"success": False, "total_itens": 0})

if __name__ == '__main__':
    app.run(debug=True)