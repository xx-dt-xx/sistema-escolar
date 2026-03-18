from django import forms
from django.utils import timezone
from datetime import date
from .models import Enrollment


class EnrollmentForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'placeholder': 'Nombre completo'})
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'placeholder': 'Fecha de nacimiento'})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'placeholder': 'Teléfono'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'Correo electrónico'})
    )
    address = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Dirección completa', 'rows': 3})
    )
    education_level = forms.ChoiceField(
        choices=Enrollment.EDUCATION_CHOICES,
        widget=forms.Select()
    )

    class Meta:
        model = Enrollment
        fields = ('full_name', 'date_of_birth', 'phone', 'email', 'address', 'education_level')

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob:
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            if age < 15:
                raise forms.ValidationError('El estudiante debe tener al menos 15 años para inscribirse.')
            if dob > today:
                raise forms.ValidationError('La fecha de nacimiento no puede ser en el futuro.')
        return dob

    def clean_email(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        email = self.cleaned_data.get('email')
        # Permitir el mismo email si el usuario ya existe (reinscripción)
        return email
