from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Perfil


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil Institucional de CheckDent'
    fields = ('rol', 'rut', 'telefono', 'especialidad', 'registro_salud')


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_rol', 'is_staff')

    def get_rol(self, instance):
        if hasattr(instance, 'perfil'):
            return instance.perfil.get_rol_display()
        return '-'
    get_rol.short_description = 'Rol'


# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Identidad Corporativa exigida por Módulo 2 (Criterio 2.1.2)
admin.site.site_header = 'Clínica CheckDent - Panel de Control'
admin.site.site_title = 'CheckDent Admin'
admin.site.index_title = 'Gestión Operativa de Recursos y Servicios'
