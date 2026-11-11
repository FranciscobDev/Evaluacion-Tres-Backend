from itertools import cycle
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


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
    """Formulario de inicio de sesión con estilos Bootstrap 5."""
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ej. admin, dr.roberto o carla.recepcion',
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
    """Formulario de registro de nuevos usuarios con RUT y teléfono para su Perfil."""
    first_name = forms.CharField(
        label="Nombres",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Valentina'})
    )
    last_name = forms.CharField(
        label="Apellidos",
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Muñoz Rojas'})
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'valentina@correo.cl'})
    )
    rut = forms.CharField(
        label="RUT",
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

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'rut', 'telefono')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario único'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Contraseña segura'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Repite tu contraseña'})

    def clean_rut(self):
        return validar_rut_chileno_perfil(self.cleaned_data.get('rut', ''))

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            user.perfil.rut = self.cleaned_data['rut']
            user.perfil.telefono = self.cleaned_data['telefono']
            user.perfil.rol = 'paciente'
            user.perfil.save()
        return user

