console.log('Arquivo carrinho-ajax.js carregado!');

document.addEventListener('DOMContentLoaded', function() {
    console.log('Carrinho AJAX carregado!');
    
    // Intercepta todos os formulários de adicionar ao carrinho
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    console.log(`Encontrados ${addToCartForms.length} formulários de carrinho`);
    
    addToCartForms.forEach((form, index) => {
        console.log(`Configurando formulário ${index + 1}:`, form);
        form.addEventListener('submit', async function(e) {
            console.log('Formulário submetido!', e);
            e.preventDefault(); // Previne o envio padrão do formulário
            
            const formData = new FormData(this);
            const button = this.querySelector('button[type="submit"]');
            const originalText = button.textContent;
            
            // Desabilita o botão e mostra loading
            button.disabled = true;
            button.textContent = 'Adicionando...';
            
            try {
                const response = await fetch('/api/carrinho/adicionar', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Mostra mensagem de sucesso
                    showMessage(data.message, 'success');
                    
                    // Atualiza o contador do carrinho se existir
                    updateCartCounter();
                    
                    // Opcional: adiciona uma animação visual
                    button.style.backgroundColor = '#4CAF50';
                    setTimeout(() => {
                        button.style.backgroundColor = '';
                    }, 1000);
                } else {
                    showMessage(data.message || 'Erro ao adicionar ao carrinho', 'error');
                }
            } catch (error) {
                console.error('Erro ao adicionar ao carrinho:', error);
                showMessage('Erro de conexão. Tente novamente.', 'error');
            } finally {
                // Reabilita o botão
                button.disabled = false;
                button.textContent = originalText;
            }
        });
    });
    
    // Função para mostrar mensagens
    function showMessage(message, type) {
        // Remove mensagens anteriores
        const existingMessage = document.querySelector('.cart-message');
        if (existingMessage) {
            existingMessage.remove();
        }
        
        // Cria nova mensagem
        const messageDiv = document.createElement('div');
        messageDiv.className = `cart-message ${type}`;
        messageDiv.textContent = message;
        messageDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
            ${type === 'success' ? 'background-color: #4CAF50;' : 'background-color: #f44336;'}
        `;
        
        // Adiciona animação CSS se não existir
        if (!document.querySelector('#cart-message-styles')) {
            const style = document.createElement('style');
            style.id = 'cart-message-styles';
            style.textContent = `
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(messageDiv);
        
        // Remove a mensagem após 3 segundos
        setTimeout(() => {
            messageDiv.style.animation = 'slideOut 0.3s ease-in';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.remove();
                }
            }, 300);
        }, 3000);
    }
    
    // Função para atualizar contador do carrinho
    async function updateCartCounter() {
        try {
            const response = await fetch('/api/carrinho/contador');
            const data = await response.json();
            
            if (data.success) {
                // Atualiza contador se existir
                const counter = document.querySelector('.cart-counter');
                if (counter) {
                    counter.textContent = data.total_itens;
                }
                
                // Atualiza contador no header se existir
                const headerCounter = document.querySelector('.header-cart-count');
                if (headerCounter) {
                    headerCounter.textContent = data.total_itens;
                }
            }
        } catch (error) {
            console.error('Erro ao atualizar contador do carrinho:', error);
        }
    }
    
    // Função para remover item do carrinho
    async function removeFromCart(itemId) {
        try {
            const formData = new FormData();
            formData.append('maquina_id', itemId);
            
            const response = await fetch('/api/carrinho/remover', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                showMessage(data.message, 'success');
                // Recarregar a página para atualizar a lista
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                showMessage(data.message || 'Erro ao remover item', 'error');
            }
        } catch (error) {
            console.error('Erro ao remover item do carrinho:', error);
            showMessage('Erro de conexão. Tente novamente.', 'error');
        }
    }
    
    // Adicionar event listeners aos botões de remover
    const removeButtons = document.querySelectorAll('.remove-item-btn');
    console.log(`Encontrados ${removeButtons.length} botões de remover`);
    
    removeButtons.forEach((button, index) => {
        console.log(`Configurando botão remover ${index + 1}:`, button);
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item-id');
            console.log(`Item ID para remover: ${itemId}`);
            
            if (confirm('Tem certeza que deseja remover este item do carrinho?')) {
                removeFromCart(itemId);
            }
        });
    });
});
