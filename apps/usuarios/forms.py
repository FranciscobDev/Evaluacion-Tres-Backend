from itertools import cycle
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Perfil


def validar_rut_chileno_perfil(rut_str):
    """Valida RUT chileno usando algoritmo Módulo 11 y retorna formato XX.XXX.XXX-X."""
    rut_limpio = rut_str.replace(".", "").replace("-", "").strip().upper()
    if len(rut_limpio) < 8 or len(rut_limpio) > 9:
        raise forms.ValidationError("El RUT debe contener entre 7 y 8 dígitos más el dígito verificador.")
    cuerpo, dv = rut_limpio[:-1], rut_limpio[-1]
    if not cuerpo.isdigit():
        raise forms.ValidationError("El cuerpo del RUT solo debe contener números.")
    factores = cycle([2, 3, 4, 5, 6, 7])
    suma = sum(int(d) * f for d, f in zip(reversed(cuerpo), factores))
    resto = 11 - (suma % 11)
    dv_esp = "0" if resto == 11 else ("K" if resto == 10 else str(resto))
    if dv != dv_esp:
        raise forms.ValidationError(f"RUT inválido (dígito verificador esperado: {dv_esp}).")
    return f"{int(cuerpo):,}".replace(",", ".") + f"-{dv}"


class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesión exclusivo para personal clínico (Odontólogos, Recepción y Admin)."""
    username = forms.CharField(
        label="Usuario Institucional",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ej. dr.mauricio, dr.ismael, dr.francisco o carla.recepcion',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': '••••••••',
        })
    )


class RegistroUsuarioForm(UserCreationForm):
    """Formulario administrativo de alta de nuevo personal clínico (Odontólogos o Recepcionistas)."""
    ROL_STAFF_CHOICES = [
        ('recepcionista', 'Recepcionista Clínico(a)'),
        ('dentista', 'Dentista / Odontólogo(a)'),
    ]

    first_name = forms.CharField(
        label="Nombres",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Francisco'})
    )
    last_name = forms.CharField(
        label="Apellidos",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Miranda'})
    )
    email = forms.EmailField(
        label="Correo Institucional",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'funcionario@checkdent.cl'})
    )
    rut = forms.CharField(
        label="RUT (Módulo 11)",
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_rut', 'placeholder': 'Ej. 12.345.678-5'})
    )
    telefono = forms.CharField(
        label="Teléfono de Contacto",
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 8765 4321'})
    )
    rol = forms.ChoiceField(
        label="Rol en la Clínica",
        choices=ROL_STAFF_CHOICES,
        initial='dentista',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    especialidad = forms.ChoiceField(
        label="Especialidad (Odontólogos)",
        choices=Perfil.ESPECIALIDADES,
        required=False,
        initial='general',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'rut', 'telefono', 'rol', 'especialidad')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. dr.apellido', 'autocomplete': 'off'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'autocomplete': 'new-password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'autocomplete': 'new-password'})

    def clean_rut(self):
        return validar_rut_chileno_perfil(self.cleaned_data.get('rut', ''))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.is_staff = True
        if commit:
            user.save()
            user.perfil.rut = self.cleaned_data['rut']
            user.perfil.telefono = self.cleaned_data['telefono']
            user.perfil.rol = self.cleaned_data['rol']
            user.perfil.especialidad = self.cleaned_data.get('especialidad') or 'general'
            user.perfil.save()
        return user
