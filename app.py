from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from banco import banco, inicializar_banco
from functools import wraps
from supabase import create_client, Client
from acessodb import supabase_url, supabase_key

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
            # Verifica se é uma requisição AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.path.startswith('/api/'):
                return jsonify({"success": False, "message": "Usuário não autenticado"}), 401
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
    
    # Aplicar desconto se houver cupom
    desconto = 0
    cupom_aplicado = session.get('cupom_aplicado')
    if cupom_aplicado:
        if cupom_aplicado['dados']['tipo'] == 'percentual':
            desconto = (total * cupom_aplicado['dados']['valor']) / 100
        else:
            desconto = min(cupom_aplicado['dados']['valor'], total)
    
    total_final = total - desconto
    
    return render_template('pages/carrinho.html', 
                         itens=itens, 
                         total=total_final,
                         subtotal=total,
                         desconto=desconto,
                         cupom_aplicado=cupom_aplicado)

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
    maquinas = [m for m in banco.listar_maquinas() if m['equipamento'].lower() == 'colheitadeira']
    return render_template('pages/ver_mais_colheitadeira.html', maquinas=maquinas)


@app.route('/ver_mais_trator')
def ver_mais_trator():
    maquinas = [m for m in banco.listar_maquinas() if m['equipamento'].lower() == 'trator']
    return render_template('pages/ver_mais_trator.html', maquinas=maquinas)

@app.route('/finaliza_pedido')
@login_required
def finaliza_pedido():
    usuario_id = session['usuario_id']
    carrinho = banco.listar_itens_carrinho(usuario_id)
    subtotal = sum(item['preco'] * item['quantidade'] for item in carrinho)
    
    # Aplicar desconto se houver cupom
    desconto = 0
    cupom_aplicado = session.get('cupom_aplicado')
    if cupom_aplicado:
        if cupom_aplicado['dados']['tipo'] == 'percentual':
            desconto = (subtotal * cupom_aplicado['dados']['valor']) / 100
        else:
            desconto = min(cupom_aplicado['dados']['valor'], subtotal)
    
    total = subtotal - desconto
    
    return render_template('pages/finaliza_pedido.html', 
                         carrinho=carrinho,
                         total=total,
                         subtotal=subtotal,
                         desconto=desconto,
                         cupom_aplicado=cupom_aplicado)

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
    print('=== CADASTRO DE MÁQUINA INICIADO ===')
    print('Usuário ID:', session.get('usuario_id'))
    print('Form data:', dict(request.form))
    print('Form files:', list(request.files.keys()))

    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return jsonify({"success": False, "message": "Usuário não logado"}), 401

    try:
        # Recebe dados do form
        cep = request.form.get("cep")
        uf = request.form.get("uf")
        numero = request.form.get("numero")
        cidade = request.form.get("cidade")
        rua = request.form.get("rua")
        referencia = request.form.get("referencia")
        modelo = request.form.get("modelo")
        equipamento = request.form.get("equipamento")
        preco_str = request.form.get("preco", "0")
        forma_aluguel = request.form.get("forma_aluguel")
        descricao = request.form.get("descricao")

        # Converter preco string para float
        preco = float(preco_str.replace("R$", "").replace(".", "").replace(",", ".").strip())

        data_maquina = {
            "usuario_id": usuario_id,
            "cep": cep,
            "uf": uf,
            "numero": numero,
            "cidade": cidade,
            "rua": rua,
            "referencia": referencia,
            "modelo_maquina": modelo,
            "equipamento": equipamento,
            "preco": preco,
            "forma_aluguel": forma_aluguel,
            "descricao": descricao
        }

        # Inserir máquina no Supabase
        print('Inserindo máquina no banco...')
        res = supabase.table("maquinas").insert(data_maquina).execute()
        if not res.data:
            raise Exception("Falha ao cadastrar máquina no banco.")

        maquina_id = res.data[0]["id"]
        print(f'Máquina cadastrada com ID: {maquina_id}')

        # Testar conectividade com Supabase Storage
        try:
            print('Testando conectividade com Supabase Storage...')
            buckets = supabase.storage.list_buckets()
            print(f'Buckets disponíveis: {[bucket.name for bucket in buckets]}')
        except Exception as e:
            print(f'Erro ao listar buckets: {e}')

        # Processar imagens se existirem
        imagens_files = request.files.getlist("imagens")
        print(f'Imagens recebidas: {len(imagens_files)}')

        uploaded_image_urls = []

        if imagens_files and imagens_files[0].filename:  # Verifica se há arquivos
            print('Processando imagens...')
            for idx, imagem_file in enumerate(imagens_files):
                print(f'Processando imagem {idx}: {imagem_file.filename}')
                if imagem_file.filename:  # Verifica se o arquivo tem nome
                    try:
                        filename = imagem_file.filename
                        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'

                        file_path = f"maquinas/{maquina_id}/imagem_{idx}_{filename}"
                        print(f'Caminho do arquivo: {file_path}')

                        file_content = imagem_file.read()
                        print(f'Tamanho do arquivo: {len(file_content)} bytes')

                        # Upload
                        print('Fazendo upload para Supabase Storage...')
                        try:
                            upload_result = supabase.storage.from_("imagens").upload(
                                file_path,
                                file_content,
                                file_options={"content-type": imagem_file.content_type}
                            )
                            print(f'Resultado do upload: {upload_result}')

                            if upload_result:
                                public_url = supabase.storage.from_("imagens").get_public_url(file_path)
                                print(f'URL pública gerada: {public_url}')
                                uploaded_image_urls.append(public_url)
                        except Exception as upload_error:
                            print(f'Erro no upload com options: {upload_error}')
                            # Tentar upload sem options
                            upload_result = supabase.storage.from_("imagens").upload(
                                file_path,
                                file_content
                            )
                            print(f'Resultado do upload (sem options): {upload_result}')
                            if upload_result:
                                public_url = supabase.storage.from_("imagens").get_public_url(file_path)
                                print(f'URL pública gerada (sem options): {public_url}')
                                uploaded_image_urls.append(public_url)

                    except Exception as e:
                        print(f"Erro ao fazer upload da imagem {idx}: {e}")
                        import traceback
                        traceback.print_exc()
                        continue
        else:
            print('Nenhuma imagem encontrada ou arquivo vazio')

        # Sempre salvar as URLs das imagens no banco se houver
        if uploaded_image_urls:
            print(f'Salvando {len(uploaded_image_urls)} URLs de imagens...')
            banco.cadastrar_imagens_maquina(maquina_id, uploaded_image_urls)

        print('=== CADASTRO CONCLUÍDO COM SUCESSO ===')
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
    try:
        print(f"=== DEBUG adicionar_ao_carrinho ===")
        print(f"Session: {session}")
        print(f"Request form: {request.form}")
        print(f"Request headers: {request.headers}")
        
        usuario_id = session['usuario_id']
        maquina_id = request.form.get('maquina_id')
        quantidade = int(request.form.get('quantidade', 1))
        forma_aluguel = request.form.get('forma_aluguel', 'DIA')
        
        print(f"usuario_id: {usuario_id}")
        print(f"maquina_id: {maquina_id}")
        print(f"quantidade: {quantidade}")
        print(f"forma_aluguel: {forma_aluguel}")
        
        if not maquina_id:
            return jsonify({"success": False, "message": "ID da máquina é obrigatório"}), 400
        
        if quantidade <= 0:
            return jsonify({"success": False, "message": "Quantidade deve ser maior que zero"}), 400
        
        maquina = banco.obter_maquina_por_id(maquina_id)
        if not maquina:
            return jsonify({"success": False, "message": "Máquina não encontrada"}), 404
        
        sucesso = banco.adicionar_ao_carrinho(usuario_id, maquina_id, quantidade, forma_aluguel)
        
        if sucesso:
            return jsonify({"success": True, "message": "Item adicionado ao carrinho com sucesso!"})
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
            return render_template('pages/carrinho.html')
        else:
            return jsonify({"success": False, "message": "Erro ao remover do carrinho"}), 500
            
    except Exception as e:
        print(f"Erro ao remover do carrinho: {e}")
        return jsonify({"success": False, "message": "Erro interno do servidor"}), 500

@app.route('/carrinho/remover/<int:item_id>', methods=['GET'])
@login_required
def carrinho_remover(item_id):
    try:
        print(f"=== DEBUG carrinho_remover ===")
        print(f"item_id recebido: {item_id}")
        
        usuario_id = session['usuario_id']
        print(f"usuario_id: {usuario_id}")
        
        sucesso = banco.remover_do_carrinho(usuario_id, item_id)
        print(f"Resultado da remoção: {sucesso}")
        
        if not sucesso:
            flash("Erro ao remover item do carrinho", "error")
        else:
            flash("Item removido do carrinho com sucesso!", "success")
            
        return redirect(url_for('carrinho'))
        
    except Exception as e:
        print(f"Erro ao remover do carrinho: {e}")
        import traceback
        traceback.print_exc()
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

            file_path = f"maquinas/{maquina_id}/b64_{idx}.{ext}"
            
            try:
                # Fazer upload para o Supabase Storage
                upload_result = supabase.storage.from_("imagens").upload(
                    file_path, 
                    file_bytes,
                    file_options={"content-type": mime_type}
                )
                
                if upload_result:
                    # Obter URL pública da imagem
                    public_url = supabase.storage.from_("imagens").get_public_url(file_path)
                    uploaded_image_urls.append(public_url)
                    
            except Exception as e:
                print(f"Erro ao fazer upload da imagem {idx}: {e}")
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

@app.route('/debug/carrinho', methods=['GET'])
@login_required
def debug_carrinho():
    try:
        usuario_id = session['usuario_id']
        print(f"=== DEBUG ROTA /debug/carrinho ===")
        print(f"usuario_id: {usuario_id}")
        
        # Lista itens do carrinho
        itens = banco.listar_itens_carrinho(usuario_id)
        
        return jsonify({
            "success": True,
            "usuario_id": usuario_id,
            "itens": itens,
            "total_itens": len(itens)
        })
        
    except Exception as e:
        print(f"Erro no debug do carrinho: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": str(e)})

####################### PEDIDOS #########################

@app.route('/api/pedido/finalizar', methods=['POST'])
@login_required
def finalizar_pedido():
    try:
        usuario_id = session['usuario_id']
        data = request.get_json()
        
        # ... (código existente para obter itens do carrinho e calcular totais)
        
        # Dados do pedido
        dados_pedido = {
            "usuario_id": usuario_id,
            "subtotal": subtotal,
            "desconto": desconto,
            "total": total,
            "metodo_pagamento": data.get('metodo_pagamento', 'PIX'),
            "parcelas": data.get('parcelas', 1), # <-- Certifique-se que este valor está sendo passado corretamente do frontend
            "status": "PENDENTE",
            "data_pedido": "now()"
        }
        
        # Inserir pedido no banco
        pedido_id = banco.criar_pedido(dados_pedido)
        if not pedido_id:
            return jsonify({"success": False, "message": "Erro ao criar pedido"}), 500
        
        # Inserir itens do pedido
        for item in itens_carrinho:
            item_pedido = {
                "pedido_id": pedido_id,
                "maquina_id": item['id'],
                "quantidade": item['quantidade'],
                "preco_unitario": item['preco'],
                "subtotal": item['subtotal']
            }
            banco.adicionar_item_pedido(item_pedido)

        # Se o pagamento for por cartão, adicione os dados (apenas os últimos 4 dígitos e nome)
        if dados_pedido['metodo_pagamento'] == 'CARTAO':
            nome_cartao = data.get('nome_cartao')
            numero_cartao_completo = data.get('numero_cartao') # NÃO ARMAZENAR ISSO EM PRODUÇÃO!
            ultimos_digitos = numero_cartao_completo[-4:] if numero_cartao_completo else None
            
            if nome_cartao and ultimos_digitos:
                banco.adicionar_cartao(usuario_id, nome_cartao, ultimos_digitos)
            else:
                print("Aviso: Dados incompletos do cartão para armazenamento.")
        
        # Limpar carrinho
        banco.limpar_carrinho(usuario_id)
        
        # Limpar cupom da sessão
        session.pop('cupom_aplicado', None)
        
        print(f"Pedido criado com sucesso! ID: {pedido_id}")
        
        return jsonify({
            "success": True,
            "message": "Pedido finalizado com sucesso!",
            "pedido_id": pedido_id
        })
        
    except Exception as e:
        print(f"Erro ao finalizar pedido: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": "Erro interno do servidor"}), 500

    

####################### CARTÕES #########################

@app.route('/meus_pedidos')
@login_required
def meus_pedidos():
    usuario_id = session['usuario_id']
    pedidos = banco.listar_pedidos_usuario(usuario_id)
    return render_template('pages/pedidos.html', pedidos=pedidos)

# Nova rota para adicionar cartão (para demonstração)
@app.route('/api/cartao/adicionar', methods=['POST'])
@login_required
def api_adicionar_cartao():
    try:
        usuario_id = session['usuario_id']
        data = request.get_json()
        
        nome_cartao = data.get('nome_cartao')
        numero_cartao = data.get('numero_cartao') # Lembre-se: NÃO SEGURO PARA PRODUÇÃO!
        
        if not nome_cartao or not numero_cartao:
            return jsonify({"success": False, "message": "Nome e número do cartão são obrigatórios."}), 400
        
        ultimos_digitos = numero_cartao[-4:]
        
        cartao_id = banco.adicionar_cartao(usuario_id, nome_cartao, ultimos_digitos)
        
        if cartao_id:
            return jsonify({"success": True, "message": "Cartão adicionado com sucesso!", "cartao_id": str(cartao_id)})
        else:
            return jsonify({"success": False, "message": "Erro ao adicionar cartão."}), 500
            
    except Exception as e:
        print(f"Erro na API de adicionar cartão: {e}")
        return jsonify({"success": False, "message": "Erro interno do servidor."}), 500

# ... (restante do código)

def metodos_pagamento(pix_mthd, cartao_methd):
    render_template('pages/carrinho.html', pix_mthd=pix_mthd, cartao_methd=cartao_methd)

if __name__ == '__main__':
    app.run(debug=True)