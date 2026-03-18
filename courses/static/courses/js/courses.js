function toggleCourse(itemId) {
    const item = document.getElementById(itemId);
    if (!item) return;

    const isExpanded = item.classList.contains('expanded');
    const btn = item.querySelector('.course-item__toggle');

    // Cerrar todos los demás items del mismo bloque
    const block = item.closest('.category-block');
    if (block) {
        block.querySelectorAll('.course-item.expanded').forEach(openItem => {
            if (openItem !== item) {
                openItem.classList.remove('expanded');
                const otherBtn = openItem.querySelector('.course-item__toggle');
                if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
            }
        });
    }

    // Toggle del item actual
    item.classList.toggle('expanded', !isExpanded);
    if (btn) btn.setAttribute('aria-expanded', String(!isExpanded));

    // Scroll suave al item si se expande
    if (!isExpanded) {
        setTimeout(() => {
            item.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 50);
    }
}
// ─── SLIDESHOW ───
(function () {
    const slideshow = document.querySelector('.slideshow');
    if (!slideshow) return;

    const slides = slideshow.querySelectorAll('.slideshow__slide');
    if (slides.length <= 1) {
        slideshow.querySelector('.slideshow__btn--prev')?.remove();
        slideshow.querySelector('.slideshow__btn--next')?.remove();
        return;
    }

    let current = 0;
    const dotsContainer = slideshow.querySelector('.slideshow__dots');

    // Crear dots
    slides.forEach((_, i) => {
        const dot = document.createElement('button');
        dot.className = 'slideshow__dot' + (i === 0 ? ' active' : '');
        dot.setAttribute('aria-label', `Imagen ${i + 1}`);
        dot.addEventListener('click', () => goTo(i));
        dotsContainer.appendChild(dot);
    });

    function goTo(index) {
        slides[current].classList.remove('active');
        dotsContainer.children[current].classList.remove('active');
        current = (index + slides.length) % slides.length;
        slides[current].classList.add('active');
        dotsContainer.children[current].classList.add('active');
    }

    slideshow.querySelector('.slideshow__btn--prev').addEventListener('click', () => { goTo(current - 1); resetTimer(); });
    slideshow.querySelector('.slideshow__btn--next').addEventListener('click', () => { goTo(current + 1); resetTimer(); });

    let timer = setInterval(() => goTo(current + 1), 4000);
    function resetTimer() {
        clearInterval(timer);
        timer = setInterval(() => goTo(current + 1), 4000);
    }
})();
