import random
import string
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_temp_password(length=10):
    """Genera una contraseña temporal aleatoria."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=length))


def get_or_create_student(full_name, email, phone, date_of_birth):
    """
    Busca un estudiante por email.
    Si no existe, crea la cuenta automáticamente con contraseña temporal.
    Retorna (user, created, temp_password)
    """
    try:
        user = User.objects.get(email=email)
        return user, False, None
    except User.DoesNotExist:
        pass

    # Generar username único a partir del email
    base_username = email.split('@')[0]
    username = base_username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f'{base_username}{counter}'
        counter += 1

    # Separar nombre y apellido
    parts = full_name.strip().split(' ', 1)
    first_name = parts[0]
    last_name = parts[1] if len(parts) > 1 else ''

    # Generar contraseña temporal
    temp_password = generate_temp_password()

    # Crear el usuario
    user = User.objects.create_user(
        username=username,
        email=email,
        password=temp_password,
        first_name=first_name,
        last_name=last_name,
        role=User.STUDENT,
        phone=phone,
        must_change_password=True,
    )

    # Crear el perfil del estudiante
    from accounts.models import StudentProfile
    StudentProfile.objects.create(
        user=user,
        date_of_birth=date_of_birth,
    )

    return user, True, temp_password


def check_schedule_conflict(student, group):
    """
    Verifica si el estudiante ya tiene un curso activo
    que se empalme con el horario del grupo que quiere inscribirse.
    Retorna lista de conflictos encontrados.
    """
    from courses.models import Schedule
    new_schedules = group.schedules.all()
    conflicts = []

    active_enrollments = student.enrollments.filter(status='active').select_related('group')

    for enrollment in active_enrollments:
        existing_schedules = enrollment.group.schedules.all()
        for new_s in new_schedules:
            for exist_s in existing_schedules:
                if new_s.day == exist_s.day:
                    # Verificar si se empalman las horas
                    if new_s.start_time < exist_s.end_time and new_s.end_time > exist_s.start_time:
                        conflicts.append({
                            'course': enrollment.group.course.name,
                            'group': enrollment.group.name,
                            'day': exist_s.get_day_display(),
                            'time': f'{exist_s.start_time:%H:%M} - {exist_s.end_time:%H:%M}',
                        })
    return conflicts
