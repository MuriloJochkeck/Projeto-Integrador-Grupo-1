document.addEventListener("DOMContentLoaded", function() {
    const carousels = document.querySelectorAll(".carousel");

    carousels.forEach(carousel => {
        const track = carousel.querySelector(".carousel-track");
        const prevBtn = carousel.querySelector(".prev");
        const nextBtn = carousel.querySelector(".next");
        const cards = carousel.querySelectorAll(".card-inicial");

        let scrollAmount = cards[0].offsetWidth * 3.2;

        setTimeout(() => {
            scrollAmount = cards[0].offsetWidth * 3.2;
        }, 50);

        nextBtn.addEventListener("click", () => {
            track.scrollBy({ left: scrollAmount, behavior: "smooth" });
        });

        prevBtn.addEventListener("click", () => {
            track.scrollBy({ left: -scrollAmount, behavior: "smooth" });
        });

        window.addEventListener("resize", () => {
            scrollAmount = cards[0].offsetWidth * 3.2;
        });
    });
});