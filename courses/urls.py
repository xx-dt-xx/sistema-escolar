from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list_view, name='course_list'),
    path('<slug:slug>/', views.course_detail_view, name='course_detail'),
    path('<slug:slug>/grupos/<int:group_id>/', views.group_detail_view, name='group_detail'),
]
