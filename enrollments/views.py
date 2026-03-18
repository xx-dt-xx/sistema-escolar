from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from courses.models import Course, CourseGroup
from .models import Enrollment
from .forms import EnrollmentForm
from .utils import get_or_create_student, check_schedule_conflict


def enrollment_form_view(request, slug, group_id):
    """Formulario de inscripción a un grupo."""
    course = get_object_or_404(Course, slug=slug, is_active=True)
    group = get_object_or_404(CourseGroup, id=group_id, course=course)

    # Verificar que el grupo esté abierto
    if group.status != CourseGroup.OPEN:
        messages.error(request, 'Este grupo no está disponible para inscripciones.')
        return redirect('courses:group_detail', slug=slug, group_id=group_id)

    # Verificar que haya lugares disponibles
    if group.is_full:
        messages.error(request, 'Este grupo no tiene lugares disponibles.')
        return redirect('courses:group_detail', slug=slug, group_id=group_id)

    # Verificar fecha límite de inscripción
    if timezone.now().date() > group.enrollment_deadline:
        messages.error(request, 'La fecha límite de inscripción ha pasado.')
        return redirect('courses:group_detail', slug=slug, group_id=group_id)

    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            full_name = form.cleaned_data['full_name']
            phone = form.cleaned_data['phone']
            date_of_birth = form.cleaned_data['date_of_birth']

            # Obtener o crear la cuenta del estudiante
            student, created, temp_password = get_or_create_student(
                full_name=full_name,
                email=email,
                phone=phone,
                date_of_birth=date_of_birth,
            )

            # Verificar si ya está inscrito en este grupo
            if Enrollment.objects.filter(student=student, group=group).exists():
                messages.error(request, 'Este estudiante ya está inscrito en este grupo.')
                return render(request, 'enrollments/enrollment_form.html', {
                    'form': form, 'course': course, 'group': group
                })

            # Verificar conflicto de horarios
            conflicts = check_schedule_conflict(student, group)
            if conflicts:
                conflict_detail = ', '.join([f"{c['course']} ({c['day']} {c['time']})" for c in conflicts])
                messages.error(request, f'Conflicto de horario con: {conflict_detail}')
                return render(request, 'enrollments/enrollment_form.html', {
                    'form': form, 'course': course, 'group': group
                })

            # Crear la inscripción
            enrollment = form.save(commit=False)
            enrollment.student = student
            enrollment.group = group
            enrollment.save()

            # Redirigir a página de confirmación con datos de acceso si es cuenta nueva
            return redirect('enrollments:confirmation', enrollment_id=enrollment.id)

    else:
        form = EnrollmentForm()

    return render(request, 'enrollments/enrollment_form.html', {
        'form': form,
        'course': course,
        'group': group,
    })


def enrollment_confirmation_view(request, enrollment_id):
    """Página de confirmación de inscripción."""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)

    # Obtener temp_password de la sesión si existe
    temp_password = request.session.pop('temp_password', None)
    student_created = request.session.pop('student_created', False)

    return render(request, 'enrollments/enrollment_confirmation.html', {
        'enrollment': enrollment,
        'temp_password': temp_password,
        'student_created': student_created,
    })


@login_required
def my_courses_view(request):
    """Lista de cursos activos del estudiante."""
    active_enrollments = request.user.enrollments.filter(
        status=Enrollment.ACTIVE
    ).select_related('group__course', 'group')

    return render(request, 'enrollments/my_courses.html', {
        'enrollments': active_enrollments,
    })


@login_required
def course_history_view(request):
    """Historial de cursos completados."""
    completed_enrollments = request.user.enrollments.filter(
        status=Enrollment.COMPLETED
    ).select_related('group__course', 'group').order_by('-enrolled_at')

    return render(request, 'enrollments/course_history.html', {
        'enrollments': completed_enrollments,
    })


def registration_page_view(request):
    """Página principal de inscripciones con wizard."""
    courses = Course.objects.filter(
        is_active=True,
        groups__status=CourseGroup.OPEN
    ).distinct().select_related('category').order_by('name')

    return render(request, 'enrollments/registration.html', {
        'courses': courses,
    })


def get_course_groups_api(request, course_id):
    """
    API que devuelve los grupos disponibles de un curso en JSON.
    Se llama dinámicamente cuando el usuario selecciona un curso.
    """
    try:
        course = Course.objects.get(id=course_id, is_active=True)
    except Course.DoesNotExist:
        return JsonResponse({'error': 'Curso no encontrado'}, status=404)

    groups = CourseGroup.objects.filter(
        course=course,
        status=CourseGroup.OPEN
    ).prefetch_related('schedules').order_by('start_date')

    groups_data = []
    for group in groups:
        schedules = [
            {
                'day': s.get_day_display(),
                'start_time': s.start_time.strftime('%H:%M'),
                'end_time': s.end_time.strftime('%H:%M'),
                'classroom': s.classroom or 'Por definir',
            }
            for s in group.schedules.all()
        ]
        groups_data.append({
            'id': group.id,
            'name': group.name,
            'course_slug': course.slug,
            'shift': group.get_shift_display(),
            'shift_key': group.shift,
            'start_date': group.start_date.strftime('%d/%m/%Y'),
            'end_date': group.end_date.strftime('%d/%m/%Y'),
            'enrollment_deadline': group.enrollment_deadline.strftime('%d/%m/%Y'),
            'available_spots': group.available_spots,
            'is_full': group.is_full,
            'schedules': schedules,
            'monthly_price': str(course.monthly_price),
        })

    return JsonResponse({
        'course_name': course.name,
        'groups': groups_data,
    })
