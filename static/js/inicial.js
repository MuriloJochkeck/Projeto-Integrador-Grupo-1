document.addEventListener("DOMContentLoaded", function() {
    const carousels = document.querySelectorAll(".carousel");

    carousels.forEach(carousel => {
        const track = carousel.querySelector(".carousel-track");
        const prevBtn = carousel.querySelector(".prev");
        const nextBtn = carousel.querySelector(".next");
        const card = carousel.querySelector(".card-inicial");

        let scrollAmount = card.offsetWidth * 3; 

        nextBtn.addEventListener("click", () => {
            track.scrollBy({ left: scrollAmount, behavior: "smooth" });
        });

        prevBtn.addEventListener("click", () => {
            track.scrollBy({ left: -scrollAmount, behavior: "smooth" });
        });

        window.addEventListener("resize", () => {
            scrollAmount = card.offsetWidth * 3;
        });
    });
});


