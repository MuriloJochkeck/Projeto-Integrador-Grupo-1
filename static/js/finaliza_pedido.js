// JavaScript para a página de finalização de pedido

let totalOriginal = 0;
let descontoAplicado = 0;
let cupomAplicado = null;

document.addEventListener('DOMContentLoaded', function() {
    // Obter o valor total da página
    const totalElement = document.querySelector('.summary-row.total span');
    if (totalElement) {
        const totalText = totalElement.textContent.replace('R$ ', '').replace(',', '.');
        totalOriginal = parseFloat(totalText);
    }
    
    // Configurar parcelamento
    configurarParcelamento();
    
    // Configurar event listeners
    configurarEventListeners();
});

function configurarParcelamento() {
    const installmentsTable = document.getElementById('installments-table');
    if (!installmentsTable) return;
    
    const total = totalOriginal - descontoAplicado;
    
    // Limpar tabela
    installmentsTable.innerHTML = '';
    
    // Gerar opções de parcelamento (1 a 12x)
    for (let i = 1; i <= 12; i++) {
        const valorParcela = total / i;
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${i}x R$ ${valorParcela.toFixed(2).replace('.', ',')}</td>
            <td><input type="radio" name="installment" value="${i}" ${i === 1 ? 'checked' : ''} /></td>
        `;
        installmentsTable.appendChild(row);
    }
}

function configurarEventListeners() {
    // Botão voltar
    const backBtn = document.querySelector('.back-btn');
    if (backBtn) {
        backBtn.addEventListener('click', function() {
            window.location.href = '/carrinho';
        });
    }
    
    // Botão finalizar pedido
    const finishBtn = document.querySelector('.finish-btn');
    if (finishBtn) {
        finishBtn.addEventListener('click', finalizarPedido);
    }
    
    // Botão adicionar cartão
    const addCardBtn = document.querySelector('.add-card-btn');
    if (addCardBtn) {
        addCardBtn.addEventListener('click', function() {
            const cardForm = document.querySelector('.card-form');
            if (cardForm) {
                cardForm.style.display = cardForm.style.display === 'none' ? 'block' : 'none';
            }
        });
    }
    
    // Botão enviar cartão
    const sendCardBtn = document.querySelector('.send-card-btn');
    if (sendCardBtn) {
        sendCardBtn.addEventListener('click', adicionarCartao);
    }
    
    // Event listener para mudança de método de pagamento
    const paymentMethods = document.querySelectorAll('input[name="payment"]');
    paymentMethods.forEach(method => {
        method.addEventListener('change', function() {
            const pixMethod = document.querySelector('.pix-method');
            const cardMethod = document.querySelector('.card-method');
            
            if (this.value === 'pix' || this.checked && this.parentElement.textContent.includes('PIX')) {
                if (pixMethod) pixMethod.style.display = 'block';
                if (cardMethod) cardMethod.style.display = 'none';
            } else {
                if (pixMethod) pixMethod.style.display = 'none';
                if (cardMethod) cardMethod.style.display = 'block';
            }
        });
    });
}

function aplicarCupom() {
    const couponInput = document.getElementById('coupon-input');
    const couponMessage = document.getElementById('coupon-message');
    const discountRow = document.getElementById('discount-row');
    const discountValue = document.getElementById('discount-value');
    const totalValue = document.getElementById('total-value');
    
    if (!couponInput || !couponInput.value.trim()) {
        mostrarMensagemCupom('Digite um código de cupom', 'error');
        return;
    }
    
    const codigoCupom = couponInput.value.trim().toUpperCase();
    
    // Simular validação de cupom (aqui você pode integrar com uma API real)
    const cuponsValidos = {
        'DESCONTO10': { tipo: 'percentual', valor: 10 },
        'DESCONTO20': { tipo: 'percentual', valor: 20 },
        'R$50': { tipo: 'fixo', valor: 50 },
        'R$100': { tipo: 'fixo', valor: 100 }
    };
    
    if (cuponsValidos[codigoCupom]) {
        const cupom = cuponsValidos[codigoCupom];
        cupomAplicado = cupom;
        
        if (cupom.tipo === 'percentual') {
            descontoAplicado = (totalOriginal * cupom.valor) / 100;
        } else {
            descontoAplicado = Math.min(cupom.valor, totalOriginal);
        }
        
        // Atualizar interface
        discountRow.style.display = 'flex';
        discountValue.textContent = `R$ ${descontoAplicado.toFixed(2).replace('.', ',')}`;
        
        const novoTotal = totalOriginal - descontoAplicado;
        totalValue.textContent = `R$ ${novoTotal.toFixed(2).replace('.', ',')}`;
        
        mostrarMensagemCupom(`Cupom aplicado! Desconto de ${cupom.tipo === 'percentual' ? cupom.valor + '%' : 'R$ ' + cupom.valor}`, 'success');
        
        // Atualizar parcelamento
        configurarParcelamento();
        
    } else {
        mostrarMensagemCupom('Cupom inválido ou expirado', 'error');
    }
}

function mostrarMensagemCupom(mensagem, tipo) {
    const couponMessage = document.getElementById('coupon-message');
    if (couponMessage) {
        couponMessage.textContent = mensagem;
        couponMessage.className = `coupon-message ${tipo}`;
        couponMessage.style.display = 'block';
        
        // Esconder mensagem após 3 segundos
        setTimeout(() => {
            couponMessage.style.display = 'none';
        }, 3000);
    }
}

function adicionarCartao() {
    const nome = document.querySelector('.card-form input[placeholder="Nome no Cartão"]').value;
    const numero = document.querySelector('.card-form input[placeholder="Número do Cartão"]').value;
    const validade = document.querySelector('.card-form input[placeholder="Data de Validade (MM/AA)"]').value;
    const cvv = document.querySelector('.card-form input[placeholder="CVV"]').value;
    
    if (!nome || !numero || !validade || !cvv) {
        alert('Preencha todos os campos do cartão');
        return;
    }
    
    // Validações básicas
    if (numero.length < 13 || numero.length > 19) {
        alert('Número do cartão inválido');
        return;
    }
    
    if (!/^\d{2}\/\d{2}$/.test(validade)) {
        alert('Data de validade deve estar no formato MM/AA');
        return;
    }
    
    if (cvv.length < 3 || cvv.length > 4) {
        alert('CVV inválido');
        return;
    }
    
    // Simular adição do cartão
    alert('Cartão adicionado com sucesso!');
    
    // Limpar formulário
    document.querySelector('.card-form').reset();
    document.querySelector('.card-form').style.display = 'none';
}

async function finalizarPedido() {
    const metodoPagamento = document.querySelector('input[name="payment"]:checked');
    const parcelas = document.querySelector('input[name="installment"]:checked');
    
    if (!metodoPagamento) {
        alert('Selecione um método de pagamento');
        return;
    }
    
    if (metodoPagamento.parentElement.textContent.includes('Cartão') && !parcelas) {
        alert('Selecione o número de parcelas');
        return;
    }
    
    // Confirmar pedido
    const confirmacao = confirm('Confirmar finalização do pedido?');
    if (!confirmacao) return;
    
    try {
        // Obter valores do resumo
        const subtotalElement = document.querySelector('.summary-row:not(.total):not(.discount) span');
        const totalElement = document.querySelector('.summary-row.total span');
        
        const subtotal = parseFloat(subtotalElement.textContent.replace('R$ ', '').replace(',', '.'));
        const total = parseFloat(totalElement.textContent.replace('R$ ', '').replace(',', '.'));
        const desconto = subtotal - total;
        
        // Dados do pedido
        const dadosPedido = {
            metodo_pagamento: metodoPagamento.parentElement.textContent.includes('PIX') ? 'PIX' : 'CARTAO',
            parcelas: parcelas ? parseInt(parcelas.value) : 1,
            subtotal: subtotal,
            desconto: desconto,
            total: total
        };
        
        // Enviar para o servidor
        const response = await fetch('/api/pedido/finalizar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(dadosPedido)
        });
        
        const resultado = await response.json();
        
        if (resultado.success) {
            alert('Pedido finalizado com sucesso! Você receberá um email de confirmação.');
            window.location.href = '/';
        } else {
            alert('Erro ao finalizar pedido: ' + resultado.message);
        }
        
    } catch (error) {
        console.error('Erro ao finalizar pedido:', error);
        alert('Erro ao finalizar pedido. Tente novamente.');
    }
}
