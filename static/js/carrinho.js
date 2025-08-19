document.addEventListener('DOMContentLoaded', function() {
  // ===== FUNÇÕES DO CARRINHO =====
  
  // Carregar e exibir itens do carrinho
  function carregarCarrinho() {
    const carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
    const productList = document.querySelector('.product-list');
    
    if (!productList) return;
    
    productList.innerHTML = '';
    
    if (carrinho.length === 0) {
      productList.innerHTML = '<p style="text-align: center; color: #666;">Carrinho vazio</p>';
      atualizarResumo(0, 0);
      return;
    }
    
    carrinho.forEach((item, index) => {
      const productItem = document.createElement('div');
      productItem.className = 'product-item';
      productItem.innerHTML = `
        <img src="${item.imagem}" alt="${item.nome}" class="product-image">
        <div class="product-info">
          <div class="product-name">${item.nome}</div>
        </div>
        <div class="quantity-control">
          <div class="quantity-buttons">
            <button class="quantity-button" data-index="${index}" data-action="decrement">-</button>
            <span class="quantity-value" id="quantity-${index}">${item.quantidade}</span>
            <button class="quantity-button" data-index="${index}" data-action="increment">+</button>
          </div>
          <div class="quantity-label">Horas</div>
        </div>
        <div class="product-price">
          <div>1x R$ ${item.preco.toFixed(2)}</div>
          <div class="price-total">Total: R$ ${(item.preco * item.quantidade).toFixed(2)}</div>
        </div>
        <button class="remove-item" data-index="${index}" style="background: #ff4444; color: white; border: none; padding: 5px 10px; border-radius: 5px; cursor: pointer;">Remover</button>
      `;
      productList.appendChild(productItem);
    });
    
    adicionarEventListenersQuantidade();
    const total = carrinho.reduce((sum, item) => sum + (item.preco * item.quantidade), 0);
    atualizarResumo(total, carrinho.length);
  }
  
  // Atualizar resumo da compra
  function atualizarResumo(subtotal, numItens) {
    const summarySubtotal = document.querySelector('.summary-row:not(.bold)');
    const summaryTotal = document.querySelector('.summary-row.bold');
    
    if (summarySubtotal && summaryTotal) {
      summarySubtotal.innerHTML = `<span>Subtotal (${numItens} itens)</span><span>R$ ${subtotal.toFixed(2)}</span>`;
      summaryTotal.innerHTML = `<span>Total</span><span>R$ ${subtotal.toFixed(2)}</span>`;
    }
  }
  
  // Adicionar event listeners aos botões de quantidade
  function adicionarEventListenersQuantidade() {
    const buttons = document.querySelectorAll('.quantity-button');
    buttons.forEach(btn => {
      btn.addEventListener('click', function() {
        const index = this.getAttribute('data-index');
        const action = this.getAttribute('data-action');
        const valueSpan = document.getElementById('quantity-' + index);
        let value = parseInt(valueSpan.textContent, 10);
        
        if (action === 'increment') {
          value = value === 8760 ? 1 : value + 1;
        } else if (action === 'decrement') {
          value = value === 1 ? 8760 : value - 1;
        }
        
        valueSpan.textContent = value;
        atualizarQuantidadeItem(index, value);
      });
    });
  }
  
  // Atualizar quantidade de um item específico
  function atualizarQuantidadeItem(index, novaQuantidade) {
    const carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
    if (carrinho[index]) {
      carrinho[index].quantidade = novaQuantidade;
      localStorage.setItem('carrinho', JSON.stringify(carrinho));
      
      // Atualizar preço total do item na tela
      const priceTotal = document.querySelector(`#quantity-${index}`).closest('.product-item').querySelector('.price-total');
      if (priceTotal) {
        priceTotal.textContent = `Total: R$ ${(carrinho[index].preco * novaQuantidade).toFixed(2)}`;
      }
      
      // Atualizar resumo
      const total = carrinho.reduce((sum, item) => sum + (item.preco * item.quantidade), 0);
      atualizarResumo(total, carrinho.length);
    }
  }
  
  // Remover item do carrinho
  function removerItem(index) {
    const carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
    carrinho.splice(index, 1);
    localStorage.setItem('carrinho', JSON.stringify(carrinho));
    carregarCarrinho();
  }
  
  // Configurar sistema de parcelamento
  function configurarParcelamento() {
    const carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
    const total = carrinho.reduce((sum, item) => sum + (item.preco * item.quantidade), 0);
    
    // Remover parcelamento anterior se existir
    const parcelamentoAnterior = document.getElementById('parcelas-select');
    if (parcelamentoAnterior) {
      parcelamentoAnterior.parentNode.remove();
    }
    
    // Criar novo seletor de parcelas
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
    
    // Inserir antes do cupom
    const cupomInput = document.querySelector('.coupon-input');
    if (cupomInput && cupomInput.parentNode) {
      cupomInput.parentNode.insertBefore(parcelamentoDiv, cupomInput);
    }
  }
  
  // Finalizar pedido
  function finalizarPedido() {
    const carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
    if (carrinho.length === 0) {
      alert('Carrinho vazio! Adicione produtos antes de finalizar.');
      return;
    }
    
    const parcelas = document.getElementById('parcelas-select')?.value || 1;
    const cupom = document.querySelector('.coupon-input')?.value || '';
    
    const pedido = {
      itens: carrinho,
      parcelas: parseInt(parcelas),
      cupom: cupom,
      data: new Date().toISOString(),
      total: carrinho.reduce((sum, item) => sum + (item.preco * item.quantidade), 0)
    };
    
    localStorage.setItem('pedidoAtual', JSON.stringify(pedido));
    window.location.href = '/finaliza_pedido';
  }
  
  // ===== EVENT LISTENERS =====
  
  // Event listener para remover itens
  document.addEventListener('click', function(e) {
    if (e.target.classList.contains('remove-item')) {
      const index = parseInt(e.target.dataset.index);
      removerItem(index);
    }
  });
  
  // Event listener para botão finalizar
  const finishButton = document.querySelector('.finish-button');
  if (finishButton) {
    finishButton.addEventListener('click', finalizarPedido);
  }
  
  // ===== INICIALIZAÇÃO =====
  
  carregarCarrinho();
  configurarParcelamento();
});

// ===== FUNÇÕES DAS MINIATURAS =====
const miniaturas = document.querySelectorAll('.miniaturas img');
const imagemPrincipal = document.querySelector('.imagem-principal img');

miniaturas.forEach(miniatura => {
  miniatura.addEventListener('click', () => {
    imagemPrincipal.src = miniatura.src;
  });
});

// ===== FUNÇÕES DAS AVALIAÇÕES =====
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

// Event listeners das avaliações
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

// ===== FUNÇÃO ADICIONAR AO CARRINHO =====
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

// ===== INICIALIZAÇÃO DAS AVALIAÇÕES =====
carregarAvaliacoesSalvas();