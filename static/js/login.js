document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('loginForm');
  if (!form) return;

  const isCadastro = form.Nome_usuario !== undefined;

  if (isCadastro) {
    const telefoneInput = form.telefone;
    const cpfInput = form.cpf;

    telefoneInput.addEventListener("input", () => {
      let value = telefoneInput.value.replace(/\D/g, "").slice(0, 11);
      let formatted = "";

      if (value.length <= 2) {
        formatted = value;
      } else if (value.length <= 7) {
        formatted = `(${value.slice(0, 2)}) ${value.slice(2)}`;
      } else {
        formatted = `(${value.slice(0, 2)}) ${value.slice(2, 7)}-${value.slice(7)}`;
      }

      telefoneInput.value = formatted;
    });

    cpfInput.addEventListener("input", () => {
      let value = cpfInput.value.replace(/\D/g, "").slice(0, 11);
      let formatted = "";

      if (value.length <= 3) {
        formatted = value;
      } else if (value.length <= 6) {
        formatted = `${value.slice(0, 3)}.${value.slice(3)}`;
      } else if (value.length <= 9) {
        formatted = `${value.slice(0, 3)}.${value.slice(3, 6)}.${value.slice(6)}`;
      } else {
        formatted = `${value.slice(0, 3)}.${value.slice(3, 6)}.${value.slice(6, 9)}-${value.slice(9)}`;
      }

      cpfInput.value = formatted;
    });
  }

  form.addEventListener('submit', (e) => {
    if (isCadastro) {
      const nome = form.Nome_usuario.value.trim();
      const telefone = form.telefone.value.trim();
      const cpf = form.cpf.value.trim();
      const email = form.Email_usuario.value.trim();
      const senha = form.senha.value;
      const confirmarSenha = form.confirmar_senha.value;

      if (!nome || !telefone || !cpf || !email || !senha || !confirmarSenha) {
        alert("Por favor, preencha todos os campos.");
        e.preventDefault();
        return;
      }

      if (!validarEmail(email)) {
        alert("Email inválido.");
        e.preventDefault();
        return;
      }

      if (senha !== confirmarSenha) {
        alert("As senhas não coincidem.");
        e.preventDefault();
        return;
      }

      alert("Cadastro realizado com sucesso!");
    } else {
      const usuario = form.usuario.value.trim();
      const senha = form.senha.value.trim();

      if (!usuario || !senha) {
        alert("Por favor, preencha todos os campos.");
        e.preventDefault();
        return;
      }

      const ehEmail = validarEmail(usuario);
      const ehTelefone = validarTelefone(usuario);

      if (!ehEmail && !ehTelefone) {
        alert("Informe um email ou telefone válido.");
        e.preventDefault();
        return;
      }

      if (!validarSenha(senha)) {
        alert("Senha deve ter ao menos 6 caracteres.");
        e.preventDefault();
        return;
      }
    }
  });

  function validarEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  function validarTelefone(valor) {
    const somenteDigitos = valor.replace(/\D/g, "");
    return /^\d{10,11}$/.test(somenteDigitos);
  }

  function validarSenha(s) {
    return typeof s === 'string' && s.length >= 6;
  }
});
