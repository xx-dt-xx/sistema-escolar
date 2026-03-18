"""
URL configuration for sistema_escolar project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from courses.views import home_view, faq_view, nosotros_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('cursos/', include('courses.urls')),
    path('inscripciones/', include('enrollments.urls')),
    path('nosotros/', nosotros_view, name='nosotros'),
    path('faq/', faq_view, name='faq'),
    path('contacto/', TemplateView.as_view(template_name='contacto.html'), name='contacto'),
    path('', home_view, name='home'),
]
