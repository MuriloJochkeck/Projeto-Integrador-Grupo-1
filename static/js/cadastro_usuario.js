 document.getElementById("cadastroForm").addEventListener("submit", function(e) {
      e.preventDefault(); // Evita envio imediato

      const nome = this.nome_user.value.trim();
      const telefone = this.telefone_user.value.trim();
      const cpf = this.cpf.value.trim();
      const email = this.email.value.trim();
      const senha = this.senha.value;
      const confirmarSenha = this.confirmar_senha.value;

      // Valida nome
      if (!/^[A-Za-zÀ-ÿ\s]+$/.test(nome)) {
        alert("O nome deve conter apenas letras.");
        return;
      }

      // Valida telefone
      if (!/^\d{10,11}$/.test(telefone)) {
        alert("O telefone deve conter apenas números (10 ou 11 dígitos).");
        return;
      }

      // Valida CPF
      if (!/^\d{11}$/.test(cpf)) {
        alert("O CPF deve conter 11 números.");
        return;
      }

      // Valida email
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        alert("Digite um email válido.");
        return;
      }

      // Valida senha
      if (senha.length < 6) {
        alert("A senha deve ter pelo menos 6 caracteres.");
        return;
      }

      if (senha !== confirmarSenha) {
        alert("As senhas não coincidem.");
        return;
      }

    });