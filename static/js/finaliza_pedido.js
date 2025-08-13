// JavaScript para a página de finalização de pedido

document.addEventListener('DOMContentLoaded', function() {
    // Carregar dados do produto do localStorage
    const produto = JSON.parse(localStorage.getItem('produtoAluguel'));
    if (produto) {
        document.getElementById('produto-imagem').src = produto.imagem;
        document.getElementById('produto-nome').textContent = produto.nome;
        document.getElementById('produto-preco').textContent = produto.preco.toFixed(2);
    }
    
    // Configurar data mínima como hoje
    const hoje = new Date().toISOString().split('T')[0];
    document.getElementById('data-inicio').min = hoje;
    document.getElementById('data-inicio').value = hoje;
    
    // Calcular dias e valor total quando as datas mudarem
    document.getElementById('data-inicio').addEventListener('change', calcularTotal);
    document.getElementById('data-fim').addEventListener('change', calcularTotal);
});

function calcularTotal() {
    const dataInicio = new Date(document.getElementById('data-inicio').value);
    const dataFim = new Date(document.getElementById('data-fim').value);
    
    if (dataInicio && dataFim && dataFim > dataInicio) {
        const diffTime = Math.abs(dataFim - dataInicio);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        document.getElementById('quantidade-dias').value = diffDays;
        
        const produto = JSON.parse(localStorage.getItem('produtoAluguel'));
        if (produto) {
            const valorTotal = produto.preco * diffDays;
            document.getElementById('valor-total').value = `R$ ${valorTotal.toFixed(2)}`;
        }
    }
}

function voltar() {
    window.history.back();
}

// Envio do formulário
document.getElementById('form-finalizacao').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Aqui você pode adicionar a lógica para enviar os dados para o servidor
    alert('Aluguel confirmado com sucesso! Você será redirecionado para a página inicial.');
    
    // Limpar localStorage e redirecionar
    localStorage.removeItem('produtoAluguel');
    window.location.href = '/';
});
