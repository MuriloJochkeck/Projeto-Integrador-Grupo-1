from supabase import create_client, Client
from acessodb import supabase_url, supabase_key

class Banco:
    def __init__(self):
        self.supabase = create_client(supabase_url, supabase_key)

    # ----------------- Usuários -----------------
    
    def listar_usuarios(self):
        try:
            res = self.supabase.table("usuarios").select("*").execute()
            return res.data
        except Exception as e:
            print(f"Erro listar_usuarios: {e}")
            return []
    
    def get_user_by_id(self, user_id):
        try:
            res = self.supabase.table("usuarios").select("*").eq("id", str(user_id)).execute()
            if res.data:
                return res.data[0]
            return None
        except Exception as e:
            print(f"Erro get_user_by_id: {e}")
            return None

    # ----------------- Máquinas -----------------

    # def cadastrar_maquina(self, cep, uf, numero, cidade, rua, referencia,
    #                       modelo_maquina, equipamento, preco, forma_aluguel, descricao=None, usuario_id=None):
    #     try:
    #         # Converte preco para float se for string
    #         if isinstance(preco, str):
    #             preco = float(preco.replace("R$", "").replace(".", "").replace(",", ".").strip())
            
    #         data = {
    #             "usuario_id": usuario_id,
    #             "cep": cep,
    #             "uf": uf,
    #             "numero": numero,
    #             "cidade": cidade,
    #             "rua": rua,
    #             "referencia": referencia,
    #             "modelo_maquina": modelo_maquina,
    #             "equipamento": equipamento,
    #             "preco": preco,
    #             "forma_aluguel": forma_aluguel,
    #             "descricao": descricao
    #         }
            
    #         # Remove campos None
    #         data = {k: v for k, v in data.items() if v is not None}
            
    #         res = self.supabase.table("maquinas").insert(data).execute()
    #         if res.data:
    #             print(f"Máquina cadastrada! ID: {res.data[0]['id']}")
    #             return res.data[0]['id']
    #         return None
    #     except Exception as e:
    #         print(f"Erro cadastrar_maquina: {e}")
    #         return None

    def cadastrar_imagens_maquina(self, maquina_id, imagens_public_urls):
        try:
            data = []
            for url in imagens_public_urls:
                data.append({
                    "maquina_id": maquina_id,
                    "imagem_url": url
                })
            
            res = self.supabase.table("imagens_maquinas").insert(data).execute()
            print(f"URLs de imagens cadastradas para máquina ID: {maquina_id}")
            return True
        except Exception as e:
            print(f"Erro cadastrar_imagens_maquina: {e}")
            return False

    def listar_maquinas(self):
        try:
            res = self.supabase.table("maquinas")\
                .select("""
                    id, modelo_maquina, equipamento, preco, forma_aluguel, 
                    descricao, imagens_maquinas(imagem_url)
                """)\
                .execute()
            
            maquinas = []
            for maquina in res.data:
                imagens = [img['imagem_url'].rstrip('?') for img in maquina.get('imagens_maquinas', [])]

                if imagens:
                    primeira_imagem = imagens[0]  
                else:
                    primeira_imagem = '/static/media/default.jpg'  

                maquinas.append({
                    'id': maquina['id'],
                    'modelo_maquina': maquina['modelo_maquina'],
                    'equipamento': maquina['equipamento'],
                    'preco': float(maquina['preco']),
                    'forma_aluguel': maquina['forma_aluguel'],
                    'descricao': maquina['descricao'],
                    'imagens': imagens,
                    'imagem': primeira_imagem
                })
            
            return maquinas 
        except Exception as e:
            print(f"Erro listar_maquinas: {e}")
            return []


    def obter_maquina_por_id(self, maquina_id):
        try:
            res = self.supabase.table("maquinas")\
                .select("""
                    id, modelo_maquina, equipamento, preco, forma_aluguel, 
                    descricao, imagens_maquinas(imagem_url)
                """)\
                .eq("id", maquina_id)\
                .execute()
            
            if res.data:
                maquina = res.data[0]
                imagens = [img['imagem_url'] for img in maquina.get('imagens_maquinas', [])]
                primeira_imagem = imagens[0] if imagens else 'media/default.jpg'
                
                return {
                    'id': maquina['id'],
                    'modelo_maquina': maquina['modelo_maquina'],
                    'equipamento': maquina['equipamento'],
                    'preco': float(maquina['preco']),
                    'forma_aluguel': maquina['forma_aluguel'],
                    'descricao': maquina['descricao'],
                    'imagem': primeira_imagem
                }
            return None
        except Exception as e:
            print(f"Erro obter_maquina_por_id: {e}")
            return None

    # ----------------- Carrinho -----------------

    def obter_carrinho_id(self, usuario_id):
        """Obtém ou cria um carrinho para o usuário"""
        try:
            # Verifica se o usuário já tem um carrinho
            res = self.supabase.table("carrinhos")\
                .select("id")\
                .eq("usuario_id", usuario_id)\
                .execute()
            
            if res.data:
                return res.data[0]['id']
            else:
                # Cria um novo carrinho
                res = self.supabase.table("carrinhos")\
                    .insert({"usuario_id": usuario_id})\
                    .execute()
                return res.data[0]['id']
        except Exception as e:
            print(f"Erro obter_carrinho_id: {e}")
            return None

    def adicionar_ao_carrinho(self, usuario_id, maquina_id, quantidade, forma_aluguel):
        """Adiciona um item ao carrinho do usuário"""
        try:
            carrinho_id = self.obter_carrinho_id(usuario_id)
            if not carrinho_id:
                return False
            
            # Verifica se o item já existe no carrinho
            res = self.supabase.table("itens_carrinho")\
                .select("id, quantidade")\
                .eq("carrinho_id", carrinho_id)\
                .eq("maquina_id", maquina_id)\
                .execute()
            
            if res.data:
                # Atualiza a quantidade
                item = res.data[0]
                nova_quantidade = item['quantidade'] + quantidade
                
                self.supabase.table("itens_carrinho")\
                    .update({"quantidade": nova_quantidade})\
                    .eq("id", item['id'])\
                    .execute()
            else:
                # Adiciona novo item
                self.supabase.table("itens_carrinho")\
                    .insert({
                        "carrinho_id": carrinho_id,
                        "maquina_id": maquina_id,
                        "quantidade": quantidade,
                        "forma_aluguel": forma_aluguel
                    })\
                    .execute()
            
            print(f"Item adicionado ao carrinho! ID: {maquina_id}")
            return True
        except Exception as e:
            print(f"Erro adicionar_ao_carrinho: {e}")
            return False

    def remover_do_carrinho(self, usuario_id, maquina_id):
        """Remove um item do carrinho do usuário"""
        try:
            carrinho_id = self.obter_carrinho_id(usuario_id)
            if not carrinho_id:
                return False
            
            self.supabase.table("itens_carrinho")\
                .delete()\
                .eq("carrinho_id", carrinho_id)\
                .eq("maquina_id", maquina_id)\
                .execute()
            
            return True
        except Exception as e:
            print(f"Erro remover_do_carrinho: {e}")
            return False

    def atualizar_quantidade_carrinho(self, usuario_id, maquina_id, nova_quantidade):
        """Atualiza a quantidade de um item no carrinho"""
        try:
            carrinho_id = self.obter_carrinho_id(usuario_id)
            if not carrinho_id:
                return False
            
            if nova_quantidade <= 0:
                # Remove o item se a quantidade for zero ou negativa
                return self.remover_do_carrinho(usuario_id, maquina_id)
            else:
                # Atualiza a quantidade
                self.supabase.table("itens_carrinho")\
                    .update({"quantidade": nova_quantidade})\
                    .eq("carrinho_id", carrinho_id)\
                    .eq("maquina_id", maquina_id)\
                    .execute()
                
                return True
        except Exception as e:
            print(f"Erro atualizar_quantidade_carrinho: {e}")
            return False

    def limpar_carrinho(self, usuario_id):
        """Remove todos os itens do carrinho do usuário"""
        try:
            carrinho_id = self.obter_carrinho_id(usuario_id)
            if not carrinho_id:
                return False
            
            self.supabase.table("itens_carrinho")\
                .delete()\
                .eq("carrinho_id", carrinho_id)\
                .execute()
            
            return True
        except Exception as e:
            print(f"Erro limpar_carrinho: {e}")
            return False

    def listar_itens_carrinho(self, usuario_id):
        """Lista todos os itens do carrinho do usuário com detalhes das máquinas"""
        try:
            carrinho_id = self.obter_carrinho_id(usuario_id)
            if not carrinho_id:
                return []
            
            res = self.supabase.table("itens_carrinho")\
                .select("""
                    id, maquina_id, quantidade, forma_aluguel,
                    maquinas!inner(modelo_maquina, preco, equipamento),
                    maquinas(imagens_maquinas(imagem_url))
                """)\
                .eq("carrinho_id", carrinho_id)\
                .execute()
            
            itens = []
            for item in res.data:
                maquina = item['maquinas']
                imagens = maquina.get('imagens_maquinas', [])
                primeira_imagem = imagens[0]['imagem_url'] if imagens else 'media/default.jpg'
                
                preco_float = float(maquina['preco'])
                itens.append({
                    'id': item['maquina_id'],
                    'item_id': item['id'],
                    'modelo_maquina': maquina['modelo_maquina'],
                    'equipamento': maquina['equipamento'],
                    'preco': preco_float,
                    'quantidade': item['quantidade'],
                    'forma_aluguel': item['forma_aluguel'],
                    'subtotal': preco_float * item['quantidade'],
                    'imagem': primeira_imagem
                })
            
            return itens
        except Exception as e:
            print(f"Erro listar_itens_carrinho: {e}")
            return []

# ----------------- Instância global -----------------
banco = Banco()

def inicializar_banco():
    """Função mantida para compatibilidade"""
    return True