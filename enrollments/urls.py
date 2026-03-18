from django.urls import path
from . import views

app_name = 'enrollments'

urlpatterns = [
    # Página de inscripciones independiente
    path('inscripciones/', views.registration_page_view, name='registration'),

    # API para obtener grupos de un curso (llamada desde JS)
    path('api/cursos/<int:course_id>/grupos/', views.get_course_groups_api, name='course_groups_api'),

    # Flujo de inscripción existente
    path('inscripcion/<slug:slug>/grupo/<int:group_id>/', views.enrollment_form_view, name='enrollment_form'),
    path('inscripcion/confirmacion/<int:enrollment_id>/', views.enrollment_confirmation_view, name='confirmation'),
    path('mis-cursos/', views.my_courses_view, name='my_courses'),
    path('mis-cursos/historial/', views.course_history_view, name='course_history'),
]
