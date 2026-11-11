from django.contrib import admin
from .models import Paciente, Cita


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('rut', 'apellidos', 'nombres', 'telefono', 'email', 'prevision', 'creado_en')
    search_fields = ('rut', 'nombres', 'apellidos', 'telefono', 'email')
    list_filter = ('prevision',)
    fieldsets = (
        ('Identificación del Paciente', {
            'fields': ('rut', 'nombres', 'apellidos', 'fecha_nacimiento')
        }),
        ('Contacto y Previsión de Salud', {
            'fields': ('telefono', 'email', 'prevision', 'alergias_antecedentes')
        }),
    )


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_fecha', 'get_hora', 'paciente', 'get_dentista', 'recepcionista', 'estado', 'fecha_creacion')
    list_filter = ('estado', 'bloque__fecha', 'bloque__dentista')
    search_fields = ('paciente__rut', 'paciente__nombres', 'paciente__apellidos', 'motivo_consulta')
    list_editable = ('estado',)
    fieldsets = (
        ('Asignación de Hora y Paciente', {
            'fields': ('bloque', 'paciente', 'recepcionista')
        }),
        ('Detalle Clínico y Estado Operativo', {
            'fields': ('motivo_consulta', 'notas_clinicas', 'estado')
        }),
    )

    def get_fecha(self, obj):
        return obj.bloque.fecha
    get_fecha.short_description = 'Fecha Cita'

    def get_hora(self, obj):
        return f"{obj.bloque.hora_inicio.strftime('%H:%M')} - {obj.bloque.hora_fin.strftime('%H:%M')}"
    get_hora.short_description = 'Horario'

    def get_dentista(self, obj):
        return obj.bloque.dentista.get_full_name() or obj.bloque.dentista.username
    get_dentista.short_description = 'Dentista'
