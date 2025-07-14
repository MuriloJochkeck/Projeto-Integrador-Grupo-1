document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    form.addEventListener('submit', function(e) {
        const usuario = form.usuario.value.trim();
        const senha = form.senha.value.trim();
        if (!usuario || !senha) {
            alert('Por favor, preencha todos os campos.');
            e.preventDefault();
        }
        
    });
}); 