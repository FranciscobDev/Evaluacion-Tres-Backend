from django.contrib import admin
from .models import BloqueDisponibilidad


@admin.register(BloqueDisponibilidad)
class BloqueDisponibilidadAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora_inicio', 'hora_fin', 'dentista', 'box_atencion', 'estado', 'creado_en')
    list_filter = ('estado', 'fecha', 'dentista', 'box_atencion')
    search_fields = ('dentista__username', 'dentista__first_name', 'dentista__last_name', 'box_atencion')
    list_editable = ('estado',)
    ordering = ('fecha', 'hora_inicio')
    fieldsets = (
        ('Profesional y Box Asignado', {
            'fields': ('dentista', 'box_atencion')
        }),
        ('Programación Horaria y Estado', {
            'fields': ('fecha', 'hora_inicio', 'hora_fin', 'estado')
        }),
    )
