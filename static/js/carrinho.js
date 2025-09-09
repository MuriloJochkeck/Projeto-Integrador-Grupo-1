document.addEventListener('DOMContentLoaded', function() {

  // Inicializa o carrinho
  carregarCarrinho();

  // Adiciona evento ao botão de finalizar pedido
  let finishButton = document.querySelector('.finish-button');
  if (finishButton) {
    finishButton.addEventListener('click', function() {
      // Verificar se há itens no carrinho
      const productList = document.querySelector('.product-list');
      const emptyMessage = productList.querySelector('p');
      
      if (emptyMessage && emptyMessage.textContent.includes('vazio')) {
        mostrarMensagem('Adicione itens ao carrinho antes de finalizar o pedido', 'error');
        return;
      }
      
      // Verificar se o total é válido
      const totalElement = document.querySelector('.summary-row.bold span');
      if (totalElement) {
        const totalText = totalElement.textContent.replace('R$ ', '').replace(',', '.');
        const total = parseFloat(totalText);
        
        if (isNaN(total) || total <= 0) {
          mostrarMensagem('Erro no cálculo do total. Recarregue a página e tente novamente.', 'error');
          return;
        }
      }
      
      // Redirecionar para finalização
      window.location.href = finishButton.getAttribute('data-url') || '/finaliza_pedido';
    });
  }

  // Adiciona evento ao campo de cupom
  const couponInput = document.querySelector('.coupon-input');
  if (couponInput) {
    couponInput.addEventListener('keypress', function(e) {
      if (e.key === 'Enter') {
        const codigo = couponInput.value.trim();
        if (codigo) {
          aplicarCupom(codigo);
        } else {
          mostrarMensagem('Digite um código de cupom', 'error');
        }
      }
    });
    
    // Adicionar botão de aplicar cupom
    const couponButton = document.createElement('button');
    couponButton.textContent = 'Aplicar';
    couponButton.className = 'coupon-button';
    couponButton.addEventListener('click', function() {
      const codigo = couponInput.value.trim();
      if (codigo) {
        aplicarCupom(codigo);
      } else {
        mostrarMensagem('Digite um código de cupom', 'error');
      }
    });
    couponInput.parentNode.appendChild(couponButton);
  }

  // Função para carregar o carrinho da API
  function carregarCarrinho() {
    adicionarEventListenersQuantidade();
    adicionarEventListenersRemover();
  }
  
   // Atualizar resumo da compra (não necessário pois é feito pelo servidor)
   function atualizarResumo(subtotal, numItens) {
  
   }
  
   // Adicionar event listeners aos botões de quantidade
   function adicionarEventListenersQuantidade() {
     // Os botões já estão configurados com o formulário para enviar ao servidor
     // Não precisamos adicionar event listeners JavaScript para isso
   }
   
   // Adicionar event listeners aos botões de remover
   function adicionarEventListenersRemover() {
     // Os links de remover já estão configurados para chamar a rota do servidor
     // Não precisamos adicionar event listeners JavaScript para isso
   }
   
   // Função para mostrar mensagens
   function mostrarMensagem(mensagem, tipo = 'info') {
     // Remover mensagem anterior se existir
     const mensagemAnterior = document.querySelector('.carrinho-mensagem');
     if (mensagemAnterior) {
       mensagemAnterior.remove();
     }
     
     // Criar nova mensagem
     const mensagemDiv = document.createElement('div');
     mensagemDiv.className = `carrinho-mensagem ${tipo}`;
     mensagemDiv.textContent = mensagem;
     
     // Adicionar ao topo do carrinho
     const cartContainer = document.querySelector('.cart-container');
     if (cartContainer) {
       cartContainer.insertBefore(mensagemDiv, cartContainer.firstChild);
       
       // Remover mensagem após 3 segundos
       setTimeout(() => {
         if (mensagemDiv.parentNode) {
           mensagemDiv.remove();
         }
       }, 3000);
     }
   }
   
   
   // Função para aplicar cupom de desconto
   function aplicarCupom(codigo) {
     if (!codigo) {
       mostrarMensagem('Digite um código de cupom', 'error');
       return;
     }
     
     // Mostrar loading
     mostrarMensagem('Aplicando cupom...', 'info');
     
     // Aplicar cupom via AJAX
     fetch('/api/carrinho/cupom', {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json',
       },
       body: JSON.stringify({ codigo: codigo.toUpperCase() })
     })
     .then(response => {
       if (!response.ok) {
         throw new Error(`HTTP error! status: ${response.status}`);
       }
       return response.json();
     })
     .then(data => {
       if (data.success) {
         mostrarMensagem('Cupom aplicado com sucesso!', 'success');
         // Recarregar página para mostrar desconto aplicado
         setTimeout(() => {
           window.location.reload();
         }, 1000);
       } else {
         mostrarMensagem(data.message || 'Cupom inválido ou expirado', 'error');
       }
     })
     .catch(error => {
       console.error('Erro ao aplicar cupom:', error);
       mostrarMensagem('Erro ao aplicar cupom. Tente novamente.', 'error');
     });
   }
   
   // Função para remover cupom
   function removerCupom() {
     mostrarMensagem('Removendo cupom...', 'info');
     
     fetch('/api/carrinho/cupom/remover', {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json',
       }
     })
     .then(response => {
       if (!response.ok) {
         throw new Error(`HTTP error! status: ${response.status}`);
       }
       return response.json();
     })
     .then(data => {
       if (data.success) {
         mostrarMensagem('Cupom removido com sucesso!', 'success');
         setTimeout(() => {
           window.location.reload();
         }, 1000);
       } else {
         mostrarMensagem(data.message || 'Erro ao remover cupom', 'error');
       }
     })
     .catch(error => {
       console.error('Erro ao remover cupom:', error);
       mostrarMensagem('Erro ao remover cupom. Tente novamente.', 'error');
     });
   }
  
    //Remover item do carrinho - Não é mais necessário, agora usamos a rota do servidor
   function removerItem(maquinaId) {
     // Esta função não é mais necessária pois a remoção é feita pelo servidor
     // Mantida apenas para compatibilidade
     window.location.href = `/carrinho/remover/${maquinaId}`;
   }
  
  
   //Configurar sistema de parcelamento
   function configurarParcelamento() {
     const carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
     const total = carrinho.reduce((sum, item) => sum + (item.preco * item.quantidade), 0);
    
      //Remover parcelamento anterior se existir
     const parcelamentoAnterior = document.getElementById('parcelas-select');
     if (parcelamentoAnterior) {
       parcelamentoAnterior.parentNode.remove();
     }
    
      //Criar novo seletor de parcelas
     const parcelamentoDiv = document.createElement('div');
     parcelamentoDiv.className = 'summary-row';
     parcelamentoDiv.innerHTML = `
       <span>Parcelas:</span>
       <select id="parcelas-select" style="padding: 5px; border-radius: 5px; border: 1px solid #aaa;">
         ${Array.from({length: 12}, (_, i) => i + 1).map(num => 
           `<option value="${num}">${num}x R$ ${(total / num).toFixed(2)}</option>`
         ).join('')}
       </select>
     `;
    
      //Inserir antes do cupom
     const cupomInput = document.querySelector('.coupon-input');
     if (cupomInput && cupomInput.parentNode) {
       cupomInput.parentNode.insertBefore(parcelamentoDiv, cupomInput);
     }
   }
  
    //Finalizar pedido
   function finalizarPedido() {
     // Agora redirecionamos diretamente para a página de finalização
     // Os dados do carrinho já estão no servidor
     const cupom = document.querySelector('.coupon-input')?.value || '';
     
     // Se tiver cupom, poderia enviar para o servidor
     if (cupom) {
       // Implementação futura: enviar cupom para o servidor
       alert('Funcionalidade de cupom em desenvolvimento!');
     }
     
     window.location.href = '/finaliza_pedido';
   }
  
    //===== EVENT LISTENERS =====
  
    //Event listener para remover itens - Não é mais necessário, agora usamos links diretos
   // Os links de remoção já estão configurados no HTML para chamar a rota do servidor
   // Este event listener não é mais necessário
  
    //Event listener para botão finalizar
   // Já adicionamos o event listener no início do arquivo
   // Não precisamos adicionar novamente
  
    //===== INICIALIZAÇÃO =====

   carregarCarrinho();
   // Não precisamos mais configurar parcelamento via JavaScript
   // pois isso será feito pelo servidor
 });

  //===== FUNÇÕES DAS MINIATURAS =====
 const miniaturas = document.querySelectorAll('.miniaturas img');
 const imagemPrincipal = document.querySelector('.imagem-principal img');

 miniaturas.forEach(miniatura => {
   miniatura.addEventListener('click', () => {
     imagemPrincipal.src = miniatura.src;
   });
 });

  //===== FUNÇÕES DAS AVALIAÇÕES =====
 const btnAvaliar = document.querySelector('.deixe-sua button');
 const popupAvaliacao = document.getElementById('popupAvaliacao');
 const estrelas = document.querySelectorAll('#estrelas span');
 const enviarAvaliacao = document.getElementById('enviarAvaliacao');
 const areaAvaliacoes = document.querySelector('.avaliacoes');
 let avaliacaoSelecionada = 0;

 function renderizarAvaliacao(usuario, nota, index) {
   const novaAvaliacao = document.createElement('div');
   novaAvaliacao.classList.add('card-avaliacoes', 'removivel');
  
   novaAvaliacao.innerHTML = `
     <div class="usuario">
       <img src="../../static/media/login/7407992-pessoa-icone-cliente-simbolo-vetor-removebg-preview.png" />
       <span><strong>${usuario}</strong></span>
     </div>
     <div class="estrelas">${'★'.repeat(nota)}${'☆'.repeat(5 - nota)}</div>
     <button class="remover-avaliacao" data-index="${index}">Remover</button>
   `;
  
   areaAvaliacoes.appendChild(novaAvaliacao);
 }

 function carregarAvaliacoesSalvas() {
   const avaliacoesSalvas = JSON.parse(localStorage.getItem('avaliacoes') || '[]');
   avaliacoesSalvas.forEach((avaliacao, index) => {
     renderizarAvaliacao(avaliacao.usuario, avaliacao.nota, index);
   });
 }

 function salvarAvaliacao(usuario, nota) {
   const avaliacoes = JSON.parse(localStorage.getItem('avaliacoes') || '[]');
   avaliacoes.push({ usuario, nota });
   localStorage.setItem('avaliacoes', JSON.stringify(avaliacoes));
 }

 function removerAvaliacao(index) {
   let avaliacoes = JSON.parse(localStorage.getItem('avaliacoes') || '[]');
   avaliacoes.splice(index, 1);
   localStorage.setItem('avaliacoes', JSON.stringify(avaliacoes));
   atualizarAvaliacoesRemoviveis();
 }

 function atualizarAvaliacoesRemoviveis() {
   const dinamicas = document.querySelectorAll('.card-avaliacoes.removivel');
   dinamicas.forEach(el => el.remove());
   carregarAvaliacoesSalvas();
 }

  //Event listeners das avaliações
 btnAvaliar?.addEventListener('click', () => {
   popupAvaliacao.style.display = 'block';
 });

 estrelas.forEach(estrela => {
   estrela.addEventListener('click', () => {
     avaliacaoSelecionada = parseInt(estrela.dataset.value);
     estrelas.forEach(e => e.classList.remove('ativo'));
     for (let i = 0; i < avaliacaoSelecionada; i++) {
       estrelas[i].classList.add('ativo');
     }
   });
 });

 enviarAvaliacao?.addEventListener('click', () => {
   if (avaliacaoSelecionada === 0) {
     alert('Selecione pelo menos uma estrela!');
     return;
   }
  
   const usuario = "Carlinhos";
   salvarAvaliacao(usuario, avaliacaoSelecionada);
   atualizarAvaliacoesRemoviveis();
  
   popupAvaliacao.style.display = 'none';
   estrelas.forEach(e => e.classList.remove('ativo'));
   avaliacaoSelecionada = 0;
 });

 areaAvaliacoes?.addEventListener('click', (e) => {
   if (e.target.classList.contains('remover-avaliacao')) {
     const index = parseInt(e.target.dataset.index);
     removerAvaliacao(index);
   }
 });

  //===== FUNÇÃO ADICIONAR AO CARRINHO =====
 const btnAdicionarCarrinho = document.querySelector('.botoes .carrinho');

 btnAdicionarCarrinho?.addEventListener('click', () => {
   const produto = {
     nome: 'Colheitadeira John Deere S790',
     imagem: '../../static/media/trator/colheitadera2.jpg',
     preco: 4490.90,
     quantidade: 1
   };
  
   const carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
   const indexExistente = carrinho.findIndex(item => item.nome === produto.nome);
  
   if (indexExistente !== -1) {
     carrinho[indexExistente].quantidade += 1;
   } else {
     carrinho.push(produto);
   }
  
   localStorage.setItem('carrinho', JSON.stringify(carrinho));
   alert('Produto adicionado ao carrinho!');
 });

  //===== INICIALIZAÇÃO DAS AVALIAÇÕES =====
 carregarAvaliacoesSalvas();


 document.addEventListener('DOMContentLoaded', () => {
     const productList = document.querySelector('.product-list');
     const subtotalEl = document.querySelector('.summary-row span:nth-child(2)');
     const totalEl = document.querySelector('.summary-row.bold span:nth-child(2)');
     const finishButton = document.querySelector('.finish-button');

     // Função para atualizar carrinho
     async function atualizarCarrinho() {
         try {
             const res = await fetch('/api/carrinho');
             const data = await res.json();
             if (!data.success) return;

             productList.innerHTML = '';
             let subtotal = 0;

             data.itens.forEach((item, index) => {
                 const totalItem = item.preco * item.quantidade;
                 subtotal += totalItem;

                 const div = document.createElement('div');
                 div.classList.add('product-item');
                 div.innerHTML = `
                     <img class="product-image" src="/${item.imagem_url}" alt="${item.nome}" />
                     <div class="product-info">
                         <div class="product-name">${item.nome}</div>
                     </div>
                     <div class="quantity-control">
                         <div class="quantity-buttons">
                             <button class="quantity-button" data-index="${index}" data-action="decrement">-</button>
                             <span class="quantity-value" id="quantity-${index}">${item.quantidade}</span>
                             <button class="quantity-button" data-index="${index}" data-action="increment">+</button>
                         </div>
                         <span class="quantity-label">${item.forma_aluguel}</span>
                     </div>
                     <div class="product-price">
                         ${item.quantidade}x R$ ${item.preco.toFixed(2)}<br/>
                         Total: <span class="price-total">R$ ${totalItem.toFixed(2)}</span>
                     </div>
                 `;
                 productList.appendChild(div);

                  //Eventos de incrementar/decrementar
                 div.querySelectorAll('.quantity-button').forEach(btn => {
                     btn.addEventListener('click', async () => {
                         let quantidade = item.quantidade;
                         if (btn.dataset.action === 'increment') quantidade++;
                         else if (btn.dataset.action === 'decrement' && quantidade > 1) quantidade--;

                          //Atualiza no servidor
                         await fetch('/api/carrinho/adicionar', {
                             method: 'POST',
                             headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                             body: `maquina_id=${item.maquina_id}&quantidade=${quantidade}&forma_aluguel=${item.forma_aluguel}`
                         });
                         atualizarCarrinho();
                     });
                 });
             });

             subtotalEl.textContent = `R$ ${subtotal.toFixed(2)}`;
             totalEl.textContent = `R$ ${subtotal.toFixed(2)}`;

         } catch (err) {
             console.error('Erro ao carregar carrinho:', err);
         }
     }

      //Botão finalizar pedido
     finishButton.addEventListener('click', () => {
         window.location.href = '/finaliza_pedido';
     });

     atualizarCarrinho();
 });
