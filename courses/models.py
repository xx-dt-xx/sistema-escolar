from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def __str__(self):
        return self.name


class Instructor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='instructor_profile'
    )
    bio = models.TextField()
    speciality = models.CharField(max_length=255)
    years_of_experience = models.PositiveIntegerField(default=0)
    linkedin_url = models.URLField(blank=True)
    profile_picture = models.ImageField(upload_to='instructors/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Instructor'
        verbose_name_plural = 'Instructores'

    def __str__(self):
        return self.user.get_full_name()


class Course(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='courses'
    )
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    objectives = models.TextField()
    requirements = models.TextField(blank=True)
    target_audience = models.TextField(blank=True)
    duration_weeks = models.PositiveIntegerField()
    hours_per_week = models.PositiveIntegerField()
    language = models.CharField(max_length=50, default='Español')
    monthly_price = models.DecimalField(max_digits=8, decimal_places=2)
    cover_image = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        ordering = ['name']

    def save(self, *args, **kwargs):
        # Genera el slug automáticamente desde el nombre
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def total_hours(self):
        return self.hours_per_week * self.duration_weeks

    @property
    def active_groups(self):
        return self.groups.filter(status__in=[CourseGroup.OPEN, CourseGroup.IN_PROGRESS])

    def __str__(self):
        return self.name


class CourseImage(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='gallery_images'
    )
    image = models.URLField()
    order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'Imagen del curso'
        verbose_name_plural = 'Imágenes del curso'
        ordering = ['order']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.pk is None:  # solo al crear
            count = CourseImage.objects.filter(course=self.course).count()
            if count >= 2:
                raise ValidationError('Un curso puede tener máximo 2 imágenes adicionales.')

    def __str__(self):
        return f'{self.course.name} — imagen {self.order}'


class CourseSyllabus(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='syllabus'
    )
    order = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Tema del temario'
        verbose_name_plural = 'Temario'
        ordering = ['order']
        unique_together = ('course', 'order')

    def __str__(self):
        return f'{self.course.name} — {self.order}. {self.title}'


class CourseGroup(models.Model):
    MORNING = 'morning'
    AFTERNOON = 'afternoon'
    SATURDAY = 'saturday'

    SHIFT_CHOICES = [
        (MORNING, 'Mañana'),
        (AFTERNOON, 'Tarde'),
        (SATURDAY, 'Sábado'),
    ]

    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (OPEN, 'Abierto'),
        (IN_PROGRESS, 'En curso'),
        (COMPLETED, 'Completado'),
        (CANCELLED, 'Cancelado'),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='groups'
    )
    name = models.CharField(max_length=150)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=OPEN)
    instructors = models.ManyToManyField(
        Instructor,
        through='CourseGroupInstructor',
        related_name='groups'
    )
    max_capacity = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    enrollment_deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Grupo'
        verbose_name_plural = 'Grupos'
        unique_together = ('course', 'name')
        ordering = ['start_date']

    @property
    def available_spots(self):
        return self.max_capacity - self.enrollments.count()

    @property
    def is_full(self):
        return self.available_spots <= 0

    @property
    def lead_instructor(self):
        try:
            return self.coursegroupinstructor_set.get(role=CourseGroupInstructor.LEAD).instructor
        except CourseGroupInstructor.DoesNotExist:
            return None

    def __str__(self):
        return f'{self.course.name} — {self.name}'


class CourseGroupInstructor(models.Model):
    LEAD = 'lead'
    ASSISTANT = 'assistant'

    ROLE_CHOICES = [
        (LEAD, 'Instructor Principal'),
        (ASSISTANT, 'Instructor Asistente'),
    ]

    group = models.ForeignKey(CourseGroup, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=LEAD)

    class Meta:
        verbose_name = 'Instructor del grupo'
        verbose_name_plural = 'Instructores del grupo'
        unique_together = ('group', 'instructor')

    def __str__(self):
        return f'{self.instructor} — {self.group} ({self.get_role_display()})'


class Schedule(models.Model):
    MONDAY = 'monday'
    TUESDAY = 'tuesday'
    WEDNESDAY = 'wednesday'
    THURSDAY = 'thursday'
    FRIDAY = 'friday'
    SATURDAY = 'saturday'

    DAY_CHOICES = [
        (MONDAY, 'Lunes'),
        (TUESDAY, 'Martes'),
        (WEDNESDAY, 'Miércoles'),
        (THURSDAY, 'Jueves'),
        (FRIDAY, 'Viernes'),
        (SATURDAY, 'Sábado'),
    ]

    group = models.ForeignKey(
        CourseGroup,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    classroom = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Horario'
        verbose_name_plural = 'Horarios'
        ordering = ['day', 'start_time']
        unique_together = ('group', 'day')

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.group.shift == CourseGroup.SATURDAY and self.day != self.SATURDAY:
            raise ValidationError('Los cursos sabatinos solo pueden tener horario el sábado.')
        if self.group.shift != CourseGroup.SATURDAY and self.day == self.SATURDAY:
            raise ValidationError('Solo los cursos sabatinos pueden tener horario el sábado.')
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError('La hora de inicio debe ser menor a la hora de fin.')

    def __str__(self):
        return f'{self.group} — {self.get_day_display()} {self.start_time:%H:%M}-{self.end_time:%H:%M}'
