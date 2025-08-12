document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('cadastroForm');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Pegar dados do formulário
    const nome = form.nome_user.value;
    const telefone = form.telefone_user.value;
    const cpf = form.cpf.value;
    const email = form.email.value;
    const senha = form.senha.value;
    const confirmarSenha = form.confirmar_senha.value;

    // Validação simples
    if (senha !== confirmarSenha) {
      alert("As senhas não coincidem!");
      return;
    }

    // Preparar dados
    const dados = {
      nome_user: nome,
      telefone_user: telefone,
      cpf: cpf,
      email: email,
      senha: senha
    };

    try {
      // Enviar para o servidor
      const response = await fetch('/api/cadastro', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(dados)
      });

      const resultado = await response.json();

      if (resultado.success) {
        alert("Cadastro realizado com sucesso!");
        form.reset();
        window.location.href = '/login';
      } else {
        alert("Erro ao cadastrar!");
      }

    } catch (error) {
      alert('Erro ao conectar com o servidor!');
    }
  });
});
