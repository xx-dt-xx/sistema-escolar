from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from .models import User, StudentProfile, TeacherProfile


class LoginForm(AuthenticationForm):
    username = forms.IntegerField(
        widget=forms.NumberInput(attrs={'placeholder': 'Código'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
    )

    error_messages = {
        'invalid_login': 'Las credenciales ingresadas no son válidas. Intenta de nuevo.',
        'inactive': 'Tu cuenta está desactivada. Contacta al administrador.',
    }

    def clean(self):
        user_id = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if user_id and password:
            try:
                user = User.objects.get(id=user_id)
                if not user.check_password(password):
                    raise forms.ValidationError(self.error_messages['invalid_login'])
                if not user.is_active:
                    raise forms.ValidationError(self.error_messages['inactive'])
                self.user_cache = user
            except User.DoesNotExist:
                raise forms.ValidationError(self.error_messages['invalid_login'])

        return self.cleaned_data


class ChangePasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Nueva contraseña'}),
        label='Nueva contraseña'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirmar nueva contraseña'}),
        label='Confirmar contraseña'
    )


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ('date_of_birth',)


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ('bio',)
