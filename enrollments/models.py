from django.db import models
from django.conf import settings
from courses.models import CourseGroup


class Enrollment(models.Model):

    ACTIVE = 'active'
    DROPPED = 'dropped'
    COMPLETED = 'completed'

    STATUS_CHOICES = [
        (ACTIVE, 'Activo'),
        (DROPPED, 'Baja'),
        (COMPLETED, 'Completado'),
    ]

    ELEMENTARY = 'elementary'
    MIDDLE     = 'middle'
    HIGH       = 'high'
    BACHELOR   = 'bachelor'
    POSTGRAD   = 'postgrad'

    EDUCATION_CHOICES = [
        (ELEMENTARY, 'Primaria'),
        (MIDDLE,     'Secundaria'),
        (HIGH,       'Preparatoria / Bachillerato'),
        (BACHELOR,   'Licenciatura'),
        (POSTGRAD,   'Posgrado'),
    ]

    # Relaciones
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    group = models.ForeignKey(
        CourseGroup,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )

    # Estado de la inscripción
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dropped_at = models.DateTimeField(null=True, blank=True)
    drop_reason = models.TextField(blank=True)

    # Datos del estudiante capturados al inscribirse
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    education_level = models.CharField(max_length=20, choices=EDUCATION_CHOICES)

    # Auditoría
    enrolled_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'
        unique_together = ('student', 'group')
        ordering = ['-enrolled_at']

    def __str__(self):
        return f'{self.student.get_full_name()} → {self.group}'
