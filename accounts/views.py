from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, ChangePasswordForm, StudentProfileForm, TeacherProfileForm
from .models import User, StudentProfile


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Si tiene contraseña temporal, forzar cambio
            if user.must_change_password:
                return redirect('accounts:change_password')
            messages.success(request, f'¡Bienvenido, {user.get_full_name()}!')
            return redirect('home')
        else:
            messages.error(request, 'Las credenciales ingresadas no son válidas.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada.')
    return redirect('accounts:login')


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            request.user.must_change_password = False
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Contraseña actualizada correctamente.')
            return redirect('accounts:profile')
    else:
        form = ChangePasswordForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def profile_view(request):
    user = request.user
    ProfileForm = StudentProfileForm if user.is_student() else TeacherProfileForm
    profile = user.student_profile if user.is_student() else user.teacher_profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'accounts/profile.html', {'form': form})
