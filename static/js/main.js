// static/js/main.js

document.addEventListener('DOMContentLoaded', () => {

    // ─── Navbar hamburger (mobile) ───
    const toggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');

    if (toggle && navLinks) {
        toggle.addEventListener('click', () => {
            navLinks.classList.toggle('open');
        });
    }

    // ─── Dropdown de Soporte ───
    document.querySelectorAll('.nav-dropdown').forEach(dropdown => {
        const btn = dropdown.querySelector('.dropdown-toggle');
        if (btn) {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                dropdown.classList.toggle('open');
                btn.setAttribute('aria-expanded', dropdown.classList.contains('open'));
            });
        }
    });

    // Cerrar dropdown al hacer click fuera
    document.addEventListener('click', () => {
        document.querySelectorAll('.nav-dropdown.open').forEach(d => {
            d.classList.remove('open');
        });
    });

});