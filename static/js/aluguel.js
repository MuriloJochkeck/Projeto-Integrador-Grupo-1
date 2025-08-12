
//miniaturas
const miniaturas = document.querySelectorAll('.miniaturas img');
const imagemPrincipal = document.querySelector('.imagem-principal img');


miniaturas.forEach(miniatura => {
    miniatura.addEventListener('click', () => {
        imagemPrincipal.src = miniatura.src;
    });
});








//avaliações

const btnAvaliar = document.querySelector('.deixe-sua button');
const popupAvaliacao = document.getElementById('popupAvaliacao');
const estrelas = document.querySelectorAll('#estrelas span');
const enviarAvaliacao = document.getElementById('enviarAvaliacao');
const areaAvaliacoes = document.querySelector('.avaliacoes');
let avaliacaoSelecionada = 0;


function renderizarAvaliacao(usuario, nota, index) {
    const novaAvaliacao = document.createElement('div');
    novaAvaliacao.classList.add('card-avaliacoes', 'removivel');


    novaAvaliacao.innerHTML = `
    <div class="usuario">
      <img src="../../static/media/login/7407992-pessoa-icone-cliente-simbolo-vetor-removebg-preview.png" />
      <span><strong>${usuario}</strong></span>
    </div>
    <div class="estrelas">${'★'.repeat(nota)}${'☆'.repeat(5 - nota)}</div>
    <button class="remover-avaliacao" data-index="${index}">Remover</button>
  `;


    areaAvaliacoes.appendChild(novaAvaliacao);
}




function carregarAvaliacoesSalvas() {
    const avaliacoesSalvas = JSON.parse(localStorage.getItem('avaliacoes') || '[]');
    avaliacoesSalvas.forEach((avaliacao, index) => {
        renderizarAvaliacao(avaliacao.usuario, avaliacao.nota, index);
    });
}




function salvarAvaliacao(usuario, nota) {
    const avaliacoes = JSON.parse(localStorage.getItem('avaliacoes') || '[]');
    avaliacoes.push({ usuario, nota });
    localStorage.setItem('avaliacoes', JSON.stringify(avaliacoes));
}




function removerAvaliacao(index) {
    let avaliacoes = JSON.parse(localStorage.getItem('avaliacoes') || '[]');
    avaliacoes.splice(index, 1);
    localStorage.setItem('avaliacoes', JSON.stringify(avaliacoes));
    atualizarAvaliacoesRemoviveis();
}


function atualizarAvaliacoesRemoviveis() {
    const dinamicas = document.querySelectorAll('.card-avaliacoes.removivel');
    dinamicas.forEach(el => el.remove());

    carregarAvaliacoesSalvas();
}




btnAvaliar.addEventListener('click', () => {
    popupAvaliacao.style.display = 'block';
});

estrelas.forEach(estrela => {
    estrela.addEventListener('click', () => {
        avaliacaoSelecionada = parseInt(estrela.dataset.value);
        estrelas.forEach(e => e.classList.remove('ativo'));
        for (let i = 0; i < avaliacaoSelecionada; i++) {
            estrelas[i].classList.add('ativo');
        }
    });
});

enviarAvaliacao.addEventListener('click', () => {
    if (avaliacaoSelecionada === 0) {
        alert('Selecione pelo menos uma estrela!');
        return;
    }

    const usuario = "Carlinhos";
    salvarAvaliacao(usuario, avaliacaoSelecionada);
    atualizarAvaliacoesRemoviveis();

    popupAvaliacao.style.display = 'none';
    estrelas.forEach(e => e.classList.remove('ativo'));
    avaliacaoSelecionada = 0;
});

areaAvaliacoes.addEventListener('click', (e) => {
    if (e.target.classList.contains('remover-avaliacao')) {
        const index = parseInt(e.target.dataset.index);
        removerAvaliacao(index);
    }
});

carregarAvaliacoesSalvas();






//mandar para carrinho
const btnAdicionarCarrinho = document.querySelector('.botoes .carrinho');

btnAdicionarCarrinho.addEventListener('click', () => {
    const produto = {
        nome: 'Colheitadeira John Deere S790',
        imagem: '../../static/media/trator/colheitadera2.jpg',
        preco: 4490.90,
        quantidade: 1
    };

    const carrinho = JSON.parse(localStorage.getItem('carrinho')) || [];
    const indexExistente = carrinho.findIndex(item => item.nome === produto.nome);
    if (indexExistente !== -1) {
        carrinho[indexExistente].quantidade += 1;
    } else {
        carrinho.push(produto);
    }

    localStorage.setItem('carrinho', JSON.stringify(carrinho));
    alert('Produto adicionado ao carrinho!');
});