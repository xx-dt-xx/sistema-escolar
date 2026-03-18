// ─── Estado global ───────────────────────────────────────────────
const state = {
    selectedCourseId:   null,
    selectedCourseName: null,
    selectedGroup:      null,   // objeto completo del grupo
};

// ─── Elementos DOM ───────────────────────────────────────────────
const courseSearch   = document.getElementById('courseSearch');
const courseList     = document.getElementById('courseList');
const courseDropdown = document.getElementById('courseDropdown');
const control        = courseDropdown.querySelector('.searchable-select__control');
const groupsSection  = document.getElementById('groupsSection');
const groupsLoading  = document.getElementById('groupsLoading');
const groupsContent  = document.getElementById('groupsContent');
const groupsGrid     = document.getElementById('groupsGrid');
const groupsSubtitle = document.getElementById('groups-subtitle');

// ─── DROPDOWN BUSCABLE ──────────────────────────────────────────

// Abrir al hacer click en el control
control.addEventListener('click', () => toggleDropdown(true));

// Filtrar opciones al escribir
courseSearch.addEventListener('input', () => {
    const q = courseSearch.value.trim().toLowerCase();
    let visible = 0;
    const options = courseList.querySelectorAll('.searchable-select__option');

    options.forEach(opt => {
        const label = opt.dataset.label.toLowerCase();
        const cat   = (opt.dataset.category || '').toLowerCase();
        const match = label.includes(q) || cat.includes(q);
        opt.hidden = !match;
        if (match) visible++;
    });

    // Mensaje "sin resultados"
    let noRes = courseList.querySelector('.searchable-select__no-results');
    if (visible === 0 && q.length > 0) {
        if (!noRes) {
            noRes = document.createElement('li');
            noRes.className = 'searchable-select__no-results';
            noRes.setAttribute('role', 'option');
            noRes.setAttribute('aria-disabled', 'true');
            noRes.textContent = 'No se encontraron cursos.';
            courseList.appendChild(noRes);
        }
        noRes.hidden = false;
    } else if (noRes) {
        noRes.hidden = true;
    }

    if (!control.classList.contains('is-open')) toggleDropdown(true);
});

// Seleccionar opción
courseList.addEventListener('click', e => {
    const opt = e.target.closest('.searchable-select__option');
    if (!opt || opt.getAttribute('aria-disabled') === 'true') return;
    selectCourse(opt.dataset.value, opt.dataset.label);
});

// Navegación por teclado en el dropdown
courseSearch.addEventListener('keydown', e => {
    if (e.key === 'Escape') { toggleDropdown(false); return; }

    const opts = [...courseList.querySelectorAll('.searchable-select__option:not([hidden])')];
    const current = courseList.querySelector('[aria-selected="true"]');
    let idx = opts.indexOf(current);

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        idx = Math.min(idx + 1, opts.length - 1);
        highlightOption(opts[idx]);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        idx = Math.max(idx - 1, 0);
        highlightOption(opts[idx]);
    } else if (e.key === 'Enter' && current) {
        e.preventDefault();
        selectCourse(current.dataset.value, current.dataset.label);
    }
});

// Cerrar al hacer click fuera
document.addEventListener('click', e => {
    if (!courseDropdown.contains(e.target)) toggleDropdown(false);
});

function toggleDropdown(open) {
    control.classList.toggle('is-open', open);
    control.setAttribute('aria-expanded', open);
    courseList.hidden = !open;
    if (open) courseSearch.focus();
}

function highlightOption(opt) {
    if (!opt) return;
    courseList.querySelectorAll('.searchable-select__option').forEach(o => o.setAttribute('aria-selected', 'false'));
    opt.setAttribute('aria-selected', 'true');
    opt.scrollIntoView({ block: 'nearest' });
}

function selectCourse(id, label) {
    state.selectedCourseId   = id;
    state.selectedCourseName = label;
    state.selectedGroup      = null;

    courseSearch.value = label;
    toggleDropdown(false);

    // Resetear selección de grupo en sidebar
    updateSidebarCourse(label);
    hideSidebarGroup();

    // Limpiar error de curso
    hideError('course');

    fetchGroups(id);
}

// ─── FETCH GRUPOS ───────────────────────────────────────────────

async function fetchGroups(courseId, preselectedGroupId = null) {
    const url = `${window.API_GROUPS_URL}${courseId}/grupos/`;

    groupsSection.hidden   = false;
    groupsLoading.hidden   = false;
    groupsContent.hidden   = true;
    groupsGrid.innerHTML   = '';

    try {
        const res  = await fetch(url);
        const data = await res.json();

        groupsLoading.hidden = true;

        groupsSubtitle.textContent = `${data.groups.length} grupo${data.groups.length > 1 ? 's' : ''} disponible${data.groups.length > 1 ? 's' : ''} para ${data.course_name}`;
        groupsContent.hidden = false;
        renderGroups(data.groups);

        if (preselectedGroupId) {
            const card = groupsGrid.querySelector(`[data-group-id="${preselectedGroupId}"]`);
            if (card && !card.disabled) {
                card.click();
            } else {
                showError('group');
            }
        } else {
            showError('group');
        }

    } catch (err) {
        groupsLoading.hidden = true;
        console.error('Error al cargar grupos:', err);
    }
}

function renderGroups(groups) {
    groupsGrid.innerHTML = '';

    groups.forEach(group => {
        const scheduleHTML = group.schedules.map(s =>
            `<span class="group-card__schedule-pill">${s.day} ${s.start_time}–${s.end_time}</span>`
        ).join('');

        const shiftClass = {
            'morning': 'shift--morning',
            'afternoon': 'shift--afternoon',
            'saturday': 'shift--saturday',
        }[group.shift_key] || '';

        const card = document.createElement('button');
        card.type = 'button';
        card.className = `group-card${group.is_full ? ' group-card--full' : ''}`;
        card.setAttribute('role', 'radio');
        card.setAttribute('aria-checked', 'false');
        card.setAttribute('aria-disabled', group.is_full ? 'true' : 'false');
        card.dataset.groupId = group.id;
        if (group.is_full) card.disabled = true;

        card.innerHTML = `
            <div class="group-card__radio" aria-hidden="true"></div>
            <div class="group-card__body">
                <div class="group-card__header">
                    <span class="group-card__name">${group.name}</span>
                    <span class="group-card__shift ${shiftClass}">${group.shift}</span>
                </div>
                <div class="group-card__meta">
                    <span>📅 ${group.start_date} – ${group.end_date}</span>
                    <span>⏰ Inscríbete antes del ${group.enrollment_deadline}</span>
                    <span>💰 $${group.monthly_price}/mes</span>
                </div>
                <div class="group-card__schedules">${scheduleHTML}</div>
                ${group.is_full
                    ? '<span class="group-card__full-badge">Sin lugares disponibles</span>'
                    : `<p class="group-card__spots">✓ ${group.available_spots} lugar${group.available_spots !== 1 ? 'es' : ''} disponible${group.available_spots !== 1 ? 's' : ''}</p>`
                }
            </div>
        `;

        card.addEventListener('click', () => selectGroup(card, group));
        groupsGrid.appendChild(card);
    });
}

function selectGroup(card, group) {
    // Deseleccionar todos
    groupsGrid.querySelectorAll('.group-card').forEach(c => {
        c.classList.remove('selected');
        c.setAttribute('aria-checked', 'false');
    });

    // Seleccionar el elegido
    card.classList.add('selected');
    card.setAttribute('aria-checked', 'true');
    state.selectedGroup = group;

    hideError('group');
    updateSidebarGroup(group);
}

// ─── SIDEBAR ────────────────────────────────────────────────────

function updateSidebarCourse(name) {
    document.getElementById('sidebarEmpty').hidden   = true;
    document.getElementById('sidebarContent').hidden = false;
    document.getElementById('sidebar-course').textContent = name;
}

function hideSidebarGroup() {
    ['sidebar-group-section','sidebar-shift-section','sidebar-dates-section',
     'sidebar-schedule-divider','sidebar-schedule-section',
     'sidebar-price-divider','sidebar-price-section','sidebar-spots']
        .forEach(id => { document.getElementById(id).hidden = true; });
}

function updateSidebarGroup(group) {
    const show = id => { document.getElementById(id).hidden = false; };

    document.getElementById('sidebar-group').textContent  = group.name;
    document.getElementById('sidebar-shift').textContent  = group.shift;
    document.getElementById('sidebar-start').textContent  = group.start_date;
    document.getElementById('sidebar-price').textContent  = `$${group.monthly_price}`;

    const scheduleHTML = group.schedules.map(s =>
        `<p style="font-size:13px;color:var(--gray-700)">${s.day}: ${s.start_time}–${s.end_time}</p>`
    ).join('');
    document.getElementById('sidebar-schedule').innerHTML = scheduleHTML;

    const spotsEl = document.getElementById('sidebar-spots');
    spotsEl.textContent = group.is_full
        ? '⚠️ Sin lugares disponibles'
        : `✓ ${group.available_spots} lugar${group.available_spots !== 1 ? 'es' : ''} disponible${group.available_spots !== 1 ? 's' : ''}`;
    spotsEl.className = `enroll-summary__spots${group.is_full ? ' enroll-summary__spots--full' : ''}`;

    ['sidebar-group-section','sidebar-shift-section','sidebar-dates-section',
     'sidebar-schedule-divider','sidebar-schedule-section',
     'sidebar-price-divider','sidebar-price-section','sidebar-spots']
        .forEach(show);
}

// ─── VALIDACIÓN Y NAVEGACIÓN ─────────────────────────────────────

function goFromStep1() {
    let valid = true;
    if (!state.selectedCourseId) { showError('course'); valid = false; }
    if (!state.selectedGroup)    { showError('group');  valid = false; }
    if (!valid) return;
    goToStep(2);
}

function goFromStep2() {
    if (!validateStep2()) return;
    populateReview();
    goToStep(3);
}

function validateStep2() {
    let valid = true;

    const rules = [
        { id: 'full_name',       msg: 'El nombre completo es obligatorio.' },
        { id: 'date_of_birth',   msg: null },  // validación especial abajo
        { id: 'phone',           msg: 'El teléfono es obligatorio.' },
        { id: 'email',           msg: null },  // validación especial abajo
        { id: 'address',         msg: 'La dirección es obligatoria.' },
        { id: 'education_level', msg: 'Selecciona tu nivel de estudios.' },
    ];

    rules.forEach(({ id, msg }) => {
        const el = document.getElementById(`id_${id}`);
        if (!el) return;
        hideError(id);

        if (id === 'date_of_birth') {
            if (!el.value) {
                showError(id, 'La fecha de nacimiento es obligatoria.'); valid = false;
            } else {
                const today = new Date(), birth = new Date(el.value);
                let age = today.getFullYear() - birth.getFullYear();
                const m = today.getMonth() - birth.getMonth();
                if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) age--;
                if (birth > today) { showError(id, 'La fecha no puede ser en el futuro.'); valid = false; }
                else if (age < 15) { showError(id, 'Debes tener al menos 15 años.'); valid = false; }
            }
        } else if (id === 'email') {
            if (!el.value.trim()) {
                showError(id, 'El correo electrónico es obligatorio.'); valid = false;
            } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(el.value)) {
                showError(id, 'Ingresa un correo válido.'); valid = false;
            }
        } else {
            if (!el.value.trim()) { showError(id, msg); valid = false; }
        }
    });

    if (!valid) {
        const firstErr = document.querySelector('#step-2 .has-error input, #step-2 .has-error select, #step-2 .has-error textarea');
        if (firstErr) firstErr.focus();
    }
    return valid;
}

function populateReview() {
    const eduSelect = document.getElementById('id_education_level');
    const eduText   = eduSelect.options[eduSelect.selectedIndex]?.text || '—';

    const scheduleText = state.selectedGroup.schedules
        .map(s => `${s.day} ${s.start_time}–${s.end_time}`)
        .join(' · ') || '—';

    document.getElementById('review-course').textContent    = state.selectedCourseName;
    document.getElementById('review-group').textContent     = state.selectedGroup.name;
    document.getElementById('review-shift').textContent     = state.selectedGroup.shift;
    document.getElementById('review-schedule').textContent  = scheduleText;
    document.getElementById('review-start').textContent     = state.selectedGroup.start_date;
    document.getElementById('review-price').textContent     = `$${state.selectedGroup.monthly_price}/mes`;
    document.getElementById('review-name').textContent      = document.getElementById('id_full_name').value;
    document.getElementById('review-dob').textContent       = formatDate(document.getElementById('id_date_of_birth').value);
    document.getElementById('review-phone').textContent     = document.getElementById('id_phone').value;
    document.getElementById('review-email').textContent     = document.getElementById('id_email').value;
    document.getElementById('review-address').textContent   = document.getElementById('id_address').value;
    document.getElementById('review-education').textContent = eduText;
}

function submitEnrollment() {
    // Rellenar form oculto
    const map = ['full_name','date_of_birth','phone','email','address','education_level'];
    map.forEach(name => {
        document.getElementById(`hidden_${name}`).value =
            document.getElementById(`id_${name}`).value;
    });

    // Apuntar el form a la URL correcta con el slug y group_id
    const form = document.getElementById('enrollForm');
    // API_GROUPS_URL = "/inscripciones/api/cursos/"
    // La URL del enrollment_form se construye con el slug y group_id
    // Se pasa desde el template via data attributes en las tarjetas
    // Nota: para obtener el slug del curso necesitamos añadirlo al response del API
    // Por ahora redirigimos a la URL del formulario existente
    form.action = `/inscripciones/inscripcion/${state.selectedGroup.course_slug}/grupo/${state.selectedGroup.id}/`;
    form.removeAttribute('aria-hidden');
    form.submit();
}

// ─── TRANSICIONES ENTRE PASOS ─────────────────────────────────────

function goToStep(stepNum) {
    [1, 2, 3].forEach(n => {
        const panel = document.getElementById(`step-${n}`);
        const ind   = document.getElementById(`step-indicator-${n}`);
        panel.hidden = n !== stepNum;
        panel.classList.toggle('active', n === stepNum);
        ind.classList.toggle('active', n === stepNum);
        ind.classList.toggle('completed', n < stepNum);
        if (n === stepNum) ind.setAttribute('aria-current', 'step');
        else ind.removeAttribute('aria-current');
    });

    const title = document.getElementById(`step${stepNum}-title`) ||
                  document.querySelector(`#step-${stepNum} .wizard-panel__title`);
    if (title) { title.setAttribute('tabindex', '-1'); title.focus(); }

    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ─── ERRORES ─────────────────────────────────────────────────────

function showError(fieldId, msg) {
    const errorEl = document.getElementById(`error-${fieldId}`);
    if (!errorEl) return;
    if (msg) {
        const msgEl = errorEl.querySelector('.error-msg');
        if (msgEl) msgEl.textContent = msg;
    }
    errorEl.hidden = false;
    const field = document.getElementById(`field-${fieldId}`) ||
                  errorEl.closest('.enroll-field, .reg-field');
    if (field) field.classList.add('has-error');
}

function hideError(fieldId) {
    const errorEl = document.getElementById(`error-${fieldId}`);
    if (!errorEl) return;
    errorEl.hidden = true;
    const field = document.getElementById(`field-${fieldId}`) ||
                  errorEl.closest('.enroll-field, .reg-field');
    if (field) field.classList.remove('has-error');
}

// ─── HELPERS ─────────────────────────────────────────────────────

function formatDate(dateStr) {
    if (!dateStr) return '—';
    const [y, m, d] = dateStr.split('-');
    return `${d}/${m}/${y}`;
}

// ─── PRESELECCIÓN POR URL PARAMS ─────────────────────────────────

(function () {
    const params    = new URLSearchParams(window.location.search);
    const courseId  = params.get('course_id');
    const groupId   = params.get('group_id');
    if (!courseId) return;

    const option = courseList.querySelector(`[data-value="${courseId}"]`);
    if (!option) return;

    const label = option.dataset.label;
    state.selectedCourseId   = courseId;
    state.selectedCourseName = label;
    courseSearch.value = label;
    updateSidebarCourse(label);
    fetchGroups(courseId, groupId);
})();