// Solo ejecutar si estamos en la página del formulario de inscripción
if (document.getElementById('enrollForm')) {
    // ─── Elementos del DOM ───
    const form        = document.getElementById('enrollForm');
    const step1Panel  = document.getElementById('step-1');
    const step2Panel  = document.getElementById('step-2');
    const stepInd1    = document.getElementById('step-indicator-1');
    const stepInd2    = document.getElementById('step-indicator-2');

    // ─── Campos del formulario ───
    const fields = {
        full_name:       () => document.querySelector('[name="full_name"]'),
        date_of_birth:   () => document.querySelector('[name="date_of_birth"]'),
        phone:           () => document.querySelector('[name="phone"]'),
        email:           () => document.querySelector('[name="email"]'),
        address:         () => document.querySelector('[name="address"]'),
        education_level: () => document.querySelector('[name="education_level"]'),
    };

    // ─── Validación del paso 1 ───
    function validateStep1() {
        let valid = true;

        // Limpiar errores previos del lado del cliente
        document.querySelectorAll('.enroll-field--client-error').forEach(el => {
            el.classList.remove('enroll-field--error', 'enroll-field--client-error');
            const prev = el.querySelector('.client-error-msg');
            if (prev) prev.remove();
        });

        function showError(input, message) {
            const field = input.closest('.enroll-field');
            if (!field) return;
            field.classList.add('enroll-field--error', 'enroll-field--client-error');
            const err = document.createElement('span');
            err.className = 'enroll-error client-error-msg';
            err.setAttribute('role', 'alert');
            err.innerHTML = `<span aria-hidden="true">✕</span> ${message}`;
            field.appendChild(err);
            valid = false;
        }

        // Nombre completo
        const name = fields.full_name();
        if (name && !name.value.trim()) showError(name, 'El nombre completo es obligatorio.');

        // Fecha de nacimiento y edad mínima
        const dob = fields.date_of_birth();
        if (dob) {
            if (!dob.value) {
                showError(dob, 'La fecha de nacimiento es obligatoria.');
            } else {
                const today = new Date();
                const birth = new Date(dob.value);
                let age = today.getFullYear() - birth.getFullYear();
                const m = today.getMonth() - birth.getMonth();
                if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
                if (age < 15) showError(dob, 'Debes tener al menos 15 años para inscribirte.');
                if (birth > today) showError(dob, 'La fecha de nacimiento no puede ser en el futuro.');
            }
        }

        // Teléfono
        const phone = fields.phone();
        if (phone && !phone.value.trim()) showError(phone, 'El teléfono es obligatorio.');

        // Email
        const email = fields.email();
        if (email) {
            if (!email.value.trim()) {
                showError(email, 'El correo electrónico es obligatorio.');
            } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value)) {
                showError(email, 'Ingresa un correo electrónico válido.');
            }
        }

        // Dirección
        const address = fields.address();
        if (address && !address.value.trim()) showError(address, 'La dirección es obligatoria.');

        // Nivel de estudios
        const edu = fields.education_level();
        if (edu && !edu.value) showError(edu, 'Selecciona tu nivel de estudios.');

        // Hacer foco en el primer error
        if (!valid) {
            const firstError = document.querySelector('.enroll-field--client-error input, .enroll-field--client-error select, .enroll-field--client-error textarea');
            if (firstError) firstError.focus();
        }

        return valid;
    }

    // ─── Pasar al paso 2 ───
    function goToStep2() {
        if (!validateStep1()) return;

        // Poblar la tarjeta de revisión
        const eduSelect = fields.education_level();
        const eduText = eduSelect
            ? eduSelect.options[eduSelect.selectedIndex]?.text || '—'
            : '—';

        document.getElementById('review-name').textContent      = fields.full_name()?.value || '—';
        document.getElementById('review-dob').textContent       = formatDate(fields.date_of_birth()?.value) || '—';
        document.getElementById('review-phone').textContent     = fields.phone()?.value || '—';
        document.getElementById('review-email').textContent     = fields.email()?.value || '—';
        document.getElementById('review-address').textContent   = fields.address()?.value || '—';
        document.getElementById('review-education').textContent = eduText;

        // Cambiar panel
        step1Panel.hidden = true;
        step1Panel.classList.remove('active');
        step2Panel.hidden = false;
        step2Panel.classList.add('active');
        step2Panel.removeAttribute('hidden');

        // Actualizar indicador
        stepInd1.classList.remove('active');
        stepInd1.classList.add('completed');
        stepInd1.removeAttribute('aria-current');
        stepInd2.classList.add('active');
        stepInd2.setAttribute('aria-current', 'step');

        // Foco accesible en el título del paso 2
        const title2 = document.getElementById('step2-title');
        if (title2) { title2.setAttribute('tabindex', '-1'); title2.focus(); }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // ─── Regresar al paso 1 ───
    function goToStep1() {
        step2Panel.hidden = true;
        step2Panel.classList.remove('active');
        step1Panel.hidden = false;
        step1Panel.classList.add('active');
        step1Panel.removeAttribute('hidden');

        stepInd2.classList.remove('active');
        stepInd1.classList.remove('completed');
        stepInd1.classList.add('active');
        stepInd1.setAttribute('aria-current', 'step');

        const title1 = document.getElementById('step1-title');
        if (title1) { title1.setAttribute('tabindex', '-1'); title1.focus(); }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // ─── Helpers ───
    function formatDate(dateStr) {
        if (!dateStr) return '—';
        const [y, m, d] = dateStr.split('-');
        return `${d}/${m}/${y}`;
    }
}