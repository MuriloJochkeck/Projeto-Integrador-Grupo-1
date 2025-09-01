from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from banco import banco, inicializar_banco
from functools import wraps
from supabase import create_client, Client
from acessodb import supabase_url, supabase_key
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

# Inicializar banco (apenas para compatibilidade)
inicializar_banco()

# Rotas básicas
@app.route('/')
def index():
    maquinas = banco.listar_maquinas()
    user = None
    if 'usuario_id' in session:
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
            user_session = supabase.auth.sign_in_with_password({"email": email, "password": senha})
            
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
            else:
                mensagem = 'Email ou senha incorretos.'
                return render_template('pages/login_usuario.html', mensagem=mensagem)

        except Exception as e:
            print(f"Erro de login: {e}")
            mensagem = 'Email ou senha incorretos.'
            return render_template('pages/login_usuario.html', mensagem=mensagem)

    return render_template('pages/login_usuario.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('usuario_nome', None)

    try:
        supabase.auth.sign_out()
    except Exception as e:
        print(f"Erro ao deslogar do Supabase: {e}")

    return redirect(url_for('index'))

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
    return render_template('pages/aluguel.html', maquinas=maquinas)

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

        if resultado.data:
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))

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


@app.route('/api/cadastro_maquinas', methods=['POST'])
@login_required
def cadastrar_maquinas():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return jsonify({"success": False, "message": "Usuário não logado"}), 401

    try:
        # ----------------- Cadastro da máquina -----------------
        data_maquina = {
            "usuario_id": usuario_id,
            "cep": request.form["cep"],
            "uf": request.form["uf"],
            "numero": request.form["numero"],
            "cidade": request.form["cidade"],
            "rua": request.form["rua"],
            "referencia": request.form.get("referencia"),
            "modelo_maquina": request.form["modelo"],
            "equipamento": request.form["equipamento"],
            "preco": float(request.form["preco"].replace("R$", "").replace(".", "").replace(",", ".").strip()),
            "forma_aluguel": request.form.get("forma_aluguel"),
            "descricao": request.form.get("descricao")
        }

        # Inserir máquina no Supabase
        res = supabase.table("maquinas").insert(data_maquina).execute()
        if not res.data:
            raise Exception("Falha ao cadastrar máquina no banco.")

        maquina_id = res.data[0]["id"]

        # ----------------- Upload das imagens -----------------
        imagens_base64 = request.form.getlist("imagens")  # Lista de Base64
        uploaded_image_urls = []

        for idx, img_b64 in enumerate(imagens_base64):
            if not img_b64.strip():
                continue

            # Separar header se existir
            if ',' in img_b64 and img_b64.lower().startswith('data:'):
                header, raw_b64 = img_b64.split(',', 1)
                mime_type = header.split(';')[0].split(':')[1]
            else:
                raw_b64 = img_b64
                mime_type = 'image/jpeg'

            ext_map = {
                'image/jpeg': 'jpg',
                'image/jpg': 'jpg',
                'image/png': 'png',
                'image/gif': 'gif',
                'image/webp': 'webp'
            }
            ext = ext_map.get(mime_type.lower(), 'jpg')

            file_bytes = base64.b64decode(raw_b64)
            path = f"maquinas/{maquina_id}/img_{idx}.{ext}"

            # Upload para o Supabase Storage
            supabase.storage.from_("imagens-maquinas").upload(path, file_bytes, content_type=mime_type)
            url = supabase.storage.from_("imagens-maquinas").get_public_url(path).public_url
            uploaded_image_urls.append(url)

        # ----------------- Inserir URLs na tabela imagens_maquinas -----------------
        if uploaded_image_urls:
            urls_data = [{"maquina_id": maquina_id, "imagem_url": url} for url in uploaded_image_urls]
            supabase.table("imagens_maquinas").insert(urls_data).execute()

        return jsonify({
            "success": True,
            "message": "Máquina cadastrada com sucesso!",
            "maquina_id": maquina_id,
            "imagens": uploaded_image_urls
        })

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
    try:
        usuario_id = session['usuario_id']
        maquina_id = request.form.get('maquina_id')
        quantidade = int(request.form.get('quantidade', 1))
        forma_aluguel = request.form.get('forma_aluguel', 'DIA')
        
        if not maquina_id:
            return jsonify({"success": False, "message": "ID da máquina é obrigatório"}), 400
        
        if quantidade <= 0:
            return jsonify({"success": False, "message": "Quantidade deve ser maior que zero"}), 400
        
        maquina = banco.obter_maquina_por_id(maquina_id)
        if not maquina:
            return jsonify({"success": False, "message": "Máquina não encontrada"}), 404
        
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
    try:
        usuario_id = session['usuario_id']
        maquina_id = request.form.get('maquina_id')
        forma_aluguel = request.form.get('forma_aluguel', 'DIA')
        acao = request.form.get('acao')
        
        itens = banco.listar_itens_carrinho(usuario_id)
        item_atual = next((item for item in itens if str(item['id']) == str(maquina_id)), None)
        
        if acao == 'increment':
            if item_atual:
                nova_quantidade = item_atual['quantidade'] + 1
                banco.atualizar_quantidade_carrinho(usuario_id, maquina_id, nova_quantidade)
            else:
                banco.adicionar_ao_carrinho(usuario_id, maquina_id, 1, forma_aluguel)
        elif acao == 'decrement':
            if item_atual and item_atual['quantidade'] > 1:
                nova_quantidade = item_atual['quantidade'] - 1
                banco.atualizar_quantidade_carrinho(usuario_id, maquina_id, nova_quantidade)
            elif item_atual:
                banco.remover_do_carrinho(usuario_id, maquina_id)
        
        return redirect(url_for('carrinho'))
        
    except Exception as e:
        print(f"Erro ao atualizar carrinho: {e}")
        flash("Erro ao atualizar carrinho", "error")
        return redirect(url_for('carrinho'))

@app.route('/api/carrinho/remover', methods=['POST'])
@login_required
def remover_do_carrinho():
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

            mime_type = 'image/jpeg'
            raw_b64 = img_b64
            if ',' in img_b64 and img_b64.lower().startswith('data:'):
                header, raw_b64 = img_b64.split(',', 1)
                try:
                    mime_type = header.split(';')[0].split(':')[1]
                except Exception:
                    mime_type = 'image/jpeg'

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
                continue

            file_path = f"{maquina_id}/b64_{idx}.{ext}"
            filename = f"img_{idx}.{ext}"

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

@app.route('/api/carrinho/atualizar', methods=['POST'])
@login_required
def atualizar_carrinho():
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
    try:
        usuario_id = session['usuario_id']
        itens = banco.listar_itens_carrinho(usuario_id)
        
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