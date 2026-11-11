from datetime import date, datetime, timedelta, time
from django import forms
from django.core.exceptions import ValidationError
from .models import BloqueDisponibilidad


class BloqueIndividualForm(forms.ModelForm):
    """
    Formulario para que el dentista publique un bloque horario individual.
    """
    class Meta:
        model = BloqueDisponibilidad
        fields = ['fecha', 'hora_inicio', 'hora_fin', 'box_atencion']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'box_atencion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Box 1 - Ortodoncia'}),
        }

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha < date.today():
            raise ValidationError("No puedes publicar disponibilidad para fechas pasadas.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')

        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de término.")

        return cleaned_data


class GenerarJornadaForm(forms.Form):
    """
    Formulario de alta productividad para generar automáticamente todos los
    bloques de una jornada médica según el intervalo deseado.
    """
    fecha = forms.DateField(
        label="Fecha de la Jornada",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    hora_inicio_jornada = forms.TimeField(
        label="Hora de Inicio",
        initial="09:00",
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    hora_fin_jornada = forms.TimeField(
        label="Hora de Término",
        initial="13:30",
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'})
    )
    duracion_bloque = forms.IntegerField(
        label="Duración de cada Cita (minutos)",
        initial=45,
        min_value=15,
        max_value=180,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    box_atencion = forms.CharField(
        label="Sillón / Box Dental",
        initial="Box 1",
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Box 1'})
    )

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha and fecha < date.today():
            raise ValidationError("No puedes generar horarios para fechas que ya pasaron.")
        return fecha

    def clean(self):
        cleaned_data = super().clean()
        h_ini = cleaned_data.get('hora_inicio_jornada')
        h_fin = cleaned_data.get('hora_fin_jornada')

        if h_ini and h_fin and h_ini >= h_fin:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de término.")

        return cleaned_data

