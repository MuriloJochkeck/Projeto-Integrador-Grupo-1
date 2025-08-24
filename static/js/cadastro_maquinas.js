document.addEventListener("DOMContentLoaded", function () {
  const btnAvancar = document.getElementById("btn-avancar-1");
  const btnVoltar = document.getElementById("btn-voltar-1");

  const pagina1 = document.querySelector(".passar1");
  const pagina2 = document.querySelector(".passar2");

  if (btnAvancar) {
    btnAvancar.addEventListener("click", function () {
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
    btnVoltar.addEventListener("click", function () {
      pagina2.style.display = "none";
      pagina1.style.display = "block";
    });
  }
});

////////////// Formatação dos campos /////////////////////


function mascaraPreco(input) {
  let valor = input.value.replace(/\D/g, ""); 
  valor = (valor / 100).toFixed(2) + ""; 
  valor = valor.replace(".", ","); 
  valor = valor.replace(/\B(?=(\d{3})+(?!\d))/g, "."); 
  input.value = "R$ " + valor;
}


function mascaraCEP(input) {
  input.value = input.value
    .replace(/\D/g, "")
    .replace(/(\d{5})(\d)/, "$1-$2")
    .slice(0, 9);
}


function mascaraUF(input) {
  input.value = input.value
    .replace(/[^a-zA-Z]/g, "")  
    .toUpperCase()
    .slice(0, 2);               
}


function mascaraNumero(input) {
  input.value = input.value
    .replace(/\D/g, ""); 
}

///// Troca pagina //////
document.addEventListener("DOMContentLoaded", function () {
  const btnAvancar = document.getElementById("btn-avancar-1");
  const btnVoltar = document.getElementById("btn-voltar-1");

  const pagina1 = document.querySelector(".passar1");
  const pagina2 = document.querySelector(".passar2");

  if (btnAvancar) {
    btnAvancar.addEventListener("click", function () {
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
    btnVoltar.addEventListener("click", function () {
      pagina2.style.display = "none";
      pagina1.style.display = "block";
    });
  }
});


//////// Adicionar imagem temporaria //////////////


document.addEventListener("DOMContentLoaded", () => {
  const inputImagens = document.getElementById("imagens");
  const preview = document.getElementById("preview-imagens");

  if (inputImagens) {
    inputImagens.addEventListener("change", () => {
      const arquivos = inputImagens.files;

      if (arquivos.length > 0) {
        preview.innerHTML = ""; // limpa preview anterior
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

      // REMOVIDO: inputImagens.value = "";
    });
  }
});



////// Validação do UF /////////////



document.addEventListener("DOMContentLoaded", () => {
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

