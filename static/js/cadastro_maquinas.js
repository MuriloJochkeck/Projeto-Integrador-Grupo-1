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
