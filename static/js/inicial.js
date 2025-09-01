document.addEventListener("DOMContentLoaded", function() {
    const carousels = document.querySelectorAll(".carousel");

    function getScrollAmount() {
        const isMobile = window.innerWidth <= 768;
        const cardWidth = document.querySelector('.card-inicial')?.offsetWidth || 0;
        const gap = window.innerWidth <= 480 ? 10 : 15; // gap menor em telas muito pequenas
        
        if (isMobile) {
            // Em telas muito pequenas, rola 1 card por vez
            if (window.innerWidth <= 480) {
                return cardWidth + gap;
            }
            // Em mobile até 768px, rola 2 cards por vez
            return (cardWidth * 2) + gap;
        } else {
            // Em desktop, mostra 3 cards por vez
            return (cardWidth * 3) + (gap * 2);
        }
    }

    carousels.forEach(carousel => {
        const track = carousel.querySelector(".carousel-track");
        const prevBtn = carousel.querySelector(".prev");
        const nextBtn = carousel.querySelector(".next");
        const cards = carousel.querySelectorAll(".card-inicial");

        let scrollAmount = getScrollAmount();

        // Aguarda um pouco para garantir que os elementos estejam renderizados
        setTimeout(() => {
            scrollAmount = getScrollAmount();
        }, 100);

        nextBtn.addEventListener("click", () => {
            scrollAmount = getScrollAmount();
            track.scrollBy({ left: scrollAmount, behavior: "smooth" });
        });

        prevBtn.addEventListener("click", () => {
            scrollAmount = getScrollAmount();
            track.scrollBy({ left: -scrollAmount, behavior: "smooth" });
        });

        // Atualiza o scrollAmount quando a janela é redimensionada
        window.addEventListener("resize", () => {
            scrollAmount = getScrollAmount();
        });
    });
});

// Função para buscar máquinas  
function buscarMaquinas(query) {
    fetch(`/search_maquinas?query=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            const resultadoDiv = document.getElementById('resultado-busca');
            resultadoDiv.innerHTML = ''; // Limpa resultados anteriores
            if (data.length === 0) {
                resultadoDiv.innerHTML = '<p>Nenhum resultado encontrado.</p>';
                return;
            }
            data.forEach(maquina => {
                const maquinaDiv = document.createElement('div');
                maquinaDiv.classList.add('card-inicial');
                maquinaDiv.innerHTML = `
                    <img src="${maquina.imagens_maquinas[0]?.imagem_url || '../static/media/inicial/placeholder.png'}" alt="${maquina.modelo_maquina}">
                    <h3>${maquina.modelo_maquina}</h3>
                    <p>Equipamento: ${maquina.equipamento}</p> 
                    <p>Preço: R$ ${maquina.preco}</p>
                    <p>Forma de Aluguel: ${maquina.forma_aluguel}</p>
                    <a href="/maquina/${maquina.id}">Ver Detalhes</a>
                `;
                resultadoDiv.appendChild(maquinaDiv);
            }
            );
        }
        )
        .catch(error => {
            console.error('Erro ao buscar máquinas:', error);
        });
}

document.getElementById('search-input').addEventListener('input', function() {
    const query = this.value;
    buscarMaquinas(query);
    if (query.trim() === '') {
        document.getElementById('resultado-busca').innerHTML = '';
    }
});
// Adiciona funcionalidade de busca ao pressionar Enter
document.getElementById('search-input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        const query = this.value;
        buscarMaquinas(query);
    }
});

// Limpa a busca ao clicar no ícone de lupa
document.querySelector('.search-icon').addEventListener('click', function() {
    const searchInput = document.getElementById('search-input');
    searchInput.value = '';
    document.getElementById('resultado-busca').innerHTML = '';
    searchInput.focus();
});