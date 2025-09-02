document.addEventListener("DOMContentLoaded", function () {
  const btnAvancar = document.getElementById("btn-avancar-1");
  const btnVoltar = document.getElementById("btn-voltar-1");

  const pagina1 = document.querySelector(".passar1");
  const pagina2 = document.querySelector(".passar2");

  ////// Troca de página //////

  if (btnAvancar) {
    btnAvancar.addEventListener("click", function (e) {
      e.preventDefault(); // Previne o comportamento padrão do botão
      
      const inputsPagina1 = pagina1.querySelectorAll("input[required]");
      let preenchido = true;

      inputsPagina1.forEach(input => {
        if (!input.value.trim()) {
          preenchido = false;
          input.classList.add("input-erro");
        } else {
          input.classList.remove("input-erro");
        }
      });

      if (!preenchido) {
        alert("Preencha todos os campos obrigatórios antes de avançar.");
        return;
      }

      pagina1.style.display = "none";
      pagina2.style.display = "block";
    });
  }

  if (btnVoltar) {
    btnVoltar.addEventListener("click", function (e) {
      e.preventDefault(); // Previne o comportamento padrão do botão
      pagina2.style.display = "none";
      pagina1.style.display = "block";
    });
  }

  ////// Mascaras //////

  window.mascaraPreco = function (input) {
    let valor = input.value.replace(/\D/g, "");
    valor = (valor / 100).toFixed(2) + "";
    valor = valor.replace(".", ",");
    valor = valor.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
    input.value = "R$ " + valor;
  };

  window.mascaraCEP = function (input) {
    input.value = input.value
      .replace(/\D/g, "")
      .replace(/(\d{5})(\d)/, "$1-$2")
      .slice(0, 9);
  };

  window.mascaraUF = function (input) {
    input.value = input.value
      .replace(/[^a-zA-Z]/g, "")
      .toUpperCase()
      .slice(0, 2);
  };

  window.mascaraNumero = function (input) {
    input.value = input.value.replace(/\D/g, "");
  };

  ////// Seleção única (Dia / Hora) //////

  document.querySelectorAll('.aluguel-opcoes button').forEach(button => {
    button.addEventListener('click', () => {
      // remove seleção de todos
      document.querySelectorAll('.aluguel-opcoes button').forEach(b => b.classList.remove('selecionado'));

      // adiciona no clicado
      button.classList.add('selecionado');

      // atualiza hidden
      document.getElementById('forma_aluguel').value = button.dataset.value;
    });
  });

  ////// Preview das imagens dentro do quadrado //////

  const inputImagens = document.getElementById("imagens");
  const preview = document.getElementById("preview-imagens");

  if (inputImagens) {
    inputImagens.addEventListener("change", () => {
      const arquivos = inputImagens.files;

      if (arquivos.length > 0) {
        // esconde o texto e o ícone na primeira seleção
        const placeholder = document.getElementById("upload-placeholder");
        if (placeholder) {
          placeholder.style.display = "none";
        }

        Array.from(arquivos).forEach(arquivo => {
          if (arquivo.type.startsWith("image/")) {
            const reader = new FileReader();
            reader.onload = (e) => {
              const img = document.createElement("img");
              img.src = e.target.result;
              preview.appendChild(img);
            };
            reader.readAsDataURL(arquivo);
          }
        });
      }
    });
  }

  ////// Validação do UF //////

  const inputUF = document.querySelector("input[name='uf']");
  const estados = [
    "AC","AL","AP","AM","BA","CE","DF","ES","GO","MA",
    "MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN",
    "RS","RO","RR","SC","SP","SE","TO"
  ];

  if (inputUF) {
    inputUF.addEventListener("blur", () => {
      const valor = inputUF.value.trim().toUpperCase();

      if (valor && !estados.includes(valor)) {
        alert("UF inválida! Digite uma sigla válida (ex: SP, RJ, SC).");
        inputUF.value = "";
        inputUF.focus();
      }
    });
  }
});

  ////// Envio do formulário //////
  
  const form = document.getElementById('form-cadastro_maquinas');
  if (form) {
    form.addEventListener('submit', async (event) => {
      event.preventDefault(); // Previne o envio padrão do formulário
      
      // Prevenir múltiplos envios
      const submitButton = form.querySelector('button[type="submit"]');
      if (submitButton.disabled) {
        return; // Já está sendo processado
      }
      
      // Desabilitar botão para evitar múltiplos cliques
      submitButton.disabled = true;
      submitButton.textContent = 'Enviando...';
      
      const formData = new FormData(form);

      // Validação dos campos obrigatórios da segunda etapa
      const inputsPagina2 = document.querySelectorAll('.passar2 input[required]');
      let preenchido = true;

      inputsPagina2.forEach(input => {
        if (!input.value.trim()) {
          preenchido = false;
          input.classList.add("input-erro");
        } else {
          input.classList.remove("input-erro");
        }
      });

      // Verificar se a forma de aluguel foi selecionada
      const formaAluguel = document.getElementById('forma_aluguel').value;
      if (!formaAluguel) {
        alert('Selecione a forma de aluguel (Dia ou Horas).');
        submitButton.disabled = false;
        submitButton.textContent = 'Finalizar Cadastro';
        return;
      }

      if (!preenchido) {
        alert('Preencha todos os campos obrigatórios antes de finalizar.');
        submitButton.disabled = false;
        submitButton.textContent = 'Finalizar Cadastro';
        return;
      }

      try {
        const response = await fetch('/api/cadastro_maquinas', {
          method: 'POST',
          body: formData  // Envia FormData diretamente, sem setar headers!
        });

        // Verificar se a resposta é um redirect (status 302)
        if (response.redirected) {
          alert('Máquina cadastrada com sucesso!');
          window.location.href = response.url;
          return;
        }

        // Se não for redirect, tentar ler como JSON
        const result = await response.json();

        if (result.success) {
          alert('Máquina cadastrada com sucesso!');
          window.location.href = '/';
        } else {
          alert('Erro: ' + result.message);
          submitButton.disabled = false;
          submitButton.textContent = 'Finalizar Cadastro';
        }
      } catch (error) {
        console.error('Erro ao enviar formulário:', error);
        alert('Erro ao cadastrar máquina. Tente novamente.');
        submitButton.disabled = false;
        submitButton.textContent = 'Finalizar Cadastro';
      }
    });
  }
