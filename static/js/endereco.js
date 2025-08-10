document.getElementById('form-endereco').addEventListener('submit', function(e) {
    e.preventDefault();
    const cep = document.getElementById('cep').value.trim();
    const numero = document.getElementById('numero').value.trim();
    const uf = document.getElementById('uf').value.trim();
    const cidade = document.getElementById('cidade').value.trim();
    const rua = document.getElementById('rua').value.trim();

    if (!cep || !numero || !uf || !cidade || !rua) {
        alert('Por favor, preencha todos os campos.');
        return;
    }
    alert('Endereço salvo com sucesso!');
});

document.getElementById('voltar').addEventListener('click', function() {
    alert('Voltando para a etapa anterior...');
}); 