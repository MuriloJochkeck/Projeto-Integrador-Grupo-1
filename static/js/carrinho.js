document.addEventListener('DOMContentLoaded', function () {
  const buttons = document.querySelectorAll('.quantity-button');
  buttons.forEach(btn => {
    btn.addEventListener('click', function () {
      const index = this.getAttribute('data-index');
      const action = this.getAttribute('data-action');
      const valueSpan = document.getElementById('quantity-' + index);
      let value = parseInt(valueSpan.textContent, 10);
      if (action === 'increment') {
        if (value === 8760) {
          value = 1;
        } else if (value < 8760) {
          value++;
        }
      } else if (action === 'decrement') {
        if (value === 1) {
          value = 8760;
        } else if (value > 1) {
          value--;
        }
      }
      valueSpan.textContent = value;
    });
  });
});

//para receber maquinas do aluguel
document.addEventListener('DOMContentLoaded', function () {
  const carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
  const listaProdutos = document.querySelector('.product-list');
  const subtotalSpan = document.querySelectorAll('.summary-row span')[1];
  const totalSpan = document.querySelectorAll('.summary-row.bold span')[1];


  listaProdutos.innerHTML = '';


  let subtotal = 0;


  carrinho.forEach((produto, index) => {
    const totalProduto = produto.preco * produto.quantidade;
    subtotal += totalProduto;


    const itemHTML = `
      <div class="product-item" data-index="${index}">
        <img class="product-image" src="${produto.imagem}" alt="${produto.nome}" />
        <div class="product-info">
          <div class="product-name">${produto.nome}</div>
        </div>
        <div class="quantity-control">
          <div class="quantity-buttons">
            <button class="quantity-button" data-index="${index}" data-action="decrement">-</button>
            <span class="quantity-value" id="quantity-${index}">${produto.quantidade}</span>
            <button class="quantity-button" data-index="${index}" data-action="increment">+</button>
          </div>
          <span class="quantity-label">Horas</span>
        </div>
        <div class="product-price">
          1x R$ ${produto.preco.toFixed(2)}<br />
          Total: <span class="price-total">R$ ${totalProduto.toFixed(2)}</span><br/>
          <button class="remover-item" data-index="${index}">Remover</button>
        </div>
      </div>
    `;


    listaProdutos.insertAdjacentHTML('beforeend', itemHTML);
  });


  subtotalSpan.textContent = `R$ ${subtotal.toFixed(2)}`;
  totalSpan.textContent = `R$ ${subtotal.toFixed(2)}`;


  const buttons = document.querySelectorAll('.quantity-button');
  buttons.forEach(btn => {
    btn.addEventListener('click', function () {
      const index = parseInt(this.getAttribute('data-index'));
      const action = this.getAttribute('data-action');


      if (action === 'increment') {
        carrinho[index].quantidade++;
      } else if (action === 'decrement') {
        carrinho[index].quantidade = Math.max(1, carrinho[index].quantidade - 1);
      }


      localStorage.setItem('carrinho', JSON.stringify(carrinho));
      location.reload();
    });
  });


  // Remover do carrinho 
  const removerBtns = document.querySelectorAll('.remover-item');
  removerBtns.forEach(btn => {
    btn.addEventListener('click', function () {
      const index = parseInt(this.getAttribute('data-index'));
      carrinho.splice(index, 1);
      localStorage.setItem('carrinho', JSON.stringify(carrinho));
      location.reload();
    });
  });
});
