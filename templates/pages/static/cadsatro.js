function avancarParaCadastroII() {
  const cep = document.getElementById('cep').value.trim();
  const uf = document.getElementById('uf').value.trim();
  const numero = document.getElementById('numero').value.trim();
  const cidade = document.getElementById('cidade').value.trim();
  const rua = document.getElementById('rua').value.trim();

  if (cep && uf && numero && cidade && rua) {

    document.getElementById('form1').style.display = 'none';
    document.getElementById('form2').style.display = 'block';
  } else {
    alert("Por favor, preencha todos os campos obrigatórios.");
  }
}

function voltarParaCadastroI() {
  document.getElementById('form2').style.display = 'none';
  document.getElementById('form1').style.display = 'block';
}
