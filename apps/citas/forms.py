from itertools import cycle
from django import forms
from .models import Paciente, Cita


def validar_rut_chileno(rut_str):
    """
    Valida un RUT chileno usando el algoritmo Módulo 11.
    Retorna el RUT formateado (ej. 12.345.678-5) o lanza forms.ValidationError.
    """
    rut_limpio = rut_str.replace(".", "").replace("-", "").strip().upper()
    if len(rut_limpio) < 8 or len(rut_limpio) > 9:
        raise forms.ValidationError("El RUT debe contener entre 7 y 8 dígitos más el dígito verificador.")

    cuerpo = rut_limpio[:-1]
    dv = rut_limpio[-1]

    if not cuerpo.isdigit():
        raise forms.ValidationError("El cuerpo del RUT solo debe contener números.")

    # Algoritmo Módulo 11
    factores = cycle([2, 3, 4, 5, 6, 7])
    suma = sum(int(digito) * factor for digito, factor in zip(reversed(cuerpo), factores))
    resto = suma % 11
    dv_calculado = 11 - resto

    if dv_calculado == 11:
        dv_esperado = "0"
    elif dv_calculado == 10:
        dv_esperado = "K"
    else:
        dv_esperado = str(dv_calculado)

    if dv != dv_esperado:
        raise forms.ValidationError(f"RUT inválido. El dígito verificador ingresado no coincide (esperado: {dv_esperado}).")

    # Formatear: ej. 12.345.678-5
    cuerpo_formateado = f"{int(cuerpo):,}".replace(",", ".")
    return f"{cuerpo_formateado}-{dv}"


class AgendarCitaForm(forms.Form):
    """
    Formulario para que el personal de recepción asigne una hora libre a un paciente.
    """
    rut = forms.CharField(
        label="RUT del Paciente",
        max_length=15,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ej. 12.345.678-5',
            'id': 'id_rut',
            'autocomplete': 'off',
        })
    )
    nombres = forms.CharField(
        label="Nombres",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. Juan Carlos',
            'id': 'id_nombres',
        })
    )
    apellidos = forms.CharField(
        label="Apellidos",
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. Pérez Díaz',
            'id': 'id_apellidos',
        })
    )
    telefono = forms.CharField(
        label="Teléfono / WhatsApp",
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. +56 9 8765 4321',
            'id': 'id_telefono',
        })
    )
    email = forms.EmailField(
        label="Correo Electrónico (Opcional)",
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'paciente@correo.cl',
            'id': 'id_email',
        })
    )
    prevision = forms.ChoiceField(
        label="Previsión de Salud",
        choices=Paciente.PREVISION_CHOICES,
        initial='particular',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_prevision',
        })
    )
    alergias_antecedentes = forms.CharField(
        label="Antecedentes Médicos / Alergias (Opcional)",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Ej. Alérgico a penicilina, hipertenso, asmático...',
            'id': 'id_alergias',
        })
    )
    motivo_consulta = forms.CharField(
        label="Motivo de la Cita Odontológica",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Ej. Dolor dental agudo, limpieza semestral, evaluación de brackets...',
        })
    )

    def clean_rut(self):
        rut_raw = self.cleaned_data.get('rut', '')
        return validar_rut_chileno(rut_raw)

