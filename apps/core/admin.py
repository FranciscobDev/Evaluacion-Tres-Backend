from django.contrib import admin
from .models import EspecialidadOdontologica, TratamientoOdontologico


@admin.register(EspecialidadOdontologica)
class EspecialidadOdontologicaAdmin(admin.ModelAdmin):
    list_display = ('codigo_area', 'nombre', 'slug', 'icono', 'activa')
    list_filter = ('activa',)
    search_fields = ('codigo_area', 'nombre', 'descripcion')
    list_editable = ('activa',)
    prepopulated_fields = {'slug': ('nombre',)}
    fieldsets = (
        ('Identificación del Área Clínica', {
            'fields': ('codigo_area', 'nombre', 'slug', 'icono')
        }),
        ('Información y Estado', {
            'fields': ('descripcion', 'activa')
        }),
    )


@admin.register(TratamientoOdontologico)
class TratamientoOdontologicoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo',
        'nombre',
        'especialidad',
        'arancel',
        'cupos_diarios',
        'duracion_minutos',
        'estado',
        'vigente',
    )
    list_filter = ('especialidad', 'estado', 'vigente')
    search_fields = ('codigo', 'nombre', 'descripcion', 'especialidad__nombre')
    list_editable = ('arancel', 'cupos_diarios', 'estado', 'vigente')
    prepopulated_fields = {'slug': ('codigo', 'nombre')}
    ordering = ('especialidad__nombre', 'codigo')

    fieldsets = (
        ('1. Identificación y Clasificación Clínica', {
            'fields': ('codigo', 'nombre', 'slug', 'especialidad')
        }),
        ('2. Detalle Descriptivo y Soporte Multimedia', {
            'fields': ('descripcion', 'indicaciones_previas', 'imagen')
        }),
        ('3. Parámetros Cuantitativos (Arancel, Duración y Cupos)', {
            'fields': ('arancel', 'duracion_minutos', 'cupos_diarios')
        }),
        ('4. Condición Operativa y Control de Vigencia', {
            'fields': ('estado', 'vigente')
        }),
    )
