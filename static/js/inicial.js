document.addEventListener("DOMContentLoaded", function() {
    const carousels = document.querySelectorAll(".carousel");

    function getScrollAmount() {
        const isMobile = window.innerWidth <= 768;
        const cardWidth = document.querySelector('.card-inicial')?.offsetWidth || 0;
        const gap = window.innerWidth <= 480 ? 10 : 15; // gap menor em telas muito pequenas
        
        if (isMobile) {
            // Em mobile, mostra 2 cards por vez
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