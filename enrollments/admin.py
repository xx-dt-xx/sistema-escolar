from django.contrib import admin
from .models import Enrollment


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'group', 'status', 'enrolled_at')
    list_filter = ('status', 'education_level', 'group__course')
    search_fields = ('full_name', 'email', 'student__username')
    readonly_fields = ('enrolled_at', 'updated_at')

    fieldsets = (
        ('Inscripción', {
            'fields': ('student', 'group', 'status', 'grade', 'dropped_at', 'drop_reason')
        }),
        ('Datos del estudiante', {
            'fields': ('full_name', 'date_of_birth', 'phone', 'email', 'address', 'education_level')
        }),
        ('Auditoría', {
            'fields': ('enrolled_at', 'updated_at'),
        }),
    )
