from django import forms
from django.core.exceptions import ValidationError
from .models import TratamientoOdontologico


class TratamientoOdontologicoForm(forms.ModelForm):
    """
    Formulario ModelForm con soporte multimedia y validaciones personalizadas
    para crear y actualizar prestaciones odontológicas en el frontend (Módulo 3 - Criterio 2.1.3).
    """
    class Meta:
        model = TratamientoOdontologico
        fields = [
            'especialidad',
            'codigo',
            'nombre',
            'descripcion',
            'indicaciones_previas',
            'arancel',
            'duracion_minutos',
            'cupos_diarios',
            'estado',
            'imagen',
            'vigente',
        ]
        widgets = {
            'especialidad': forms.Select(attrs={'class': 'form-select'}),
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. TRT-ORT-001'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Instalación de Brackets Zafiro'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe el procedimiento odontológico y sus beneficios clínicos...'
            }),
            'indicaciones_previas': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej. Requiere radiografía panorámica previa.'
            }),
            'arancel': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Ej. 45000'
            }),
            'duracion_minutos': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 15,
                'placeholder': 'Ej. 45'
            }),
            'cupos_diarios': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'placeholder': 'Ej. 5'
            }),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'vigente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_codigo(self):
        codigo = (self.cleaned_data.get('codigo') or '').strip().upper()
        if len(codigo) < 4:
            raise ValidationError("El código identificador debe tener al menos 4 caracteres.")
        qs = TratamientoOdontologico.objects.filter(codigo__iexact=codigo)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError(f"Ya existe otro tratamiento registrado con el código '{codigo}'.")
        return codigo

    def clean_arancel(self):
        arancel = self.cleaned_data.get('arancel')
        if arancel is None or arancel < 0:
            raise ValidationError("El arancel clínico no puede ser un valor negativo.")
        return arancel

    def clean_cupos_diarios(self):
        cupos = self.cleaned_data.get('cupos_diarios')
        if cupos is None or cupos < 0:
            raise ValidationError("Los cupos diarios no pueden ser negativos.")
        return cupos

