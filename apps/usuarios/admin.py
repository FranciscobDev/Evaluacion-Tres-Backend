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

    def save_formset(self, request, form, formset, change):
        """
        Evita el error de integridad UNIQUE constraint en Perfil al añadir un usuario:
        si la señal post_save ya creó el registro de perfil, asigna su clave primaria
        para que Django ejecute un UPDATE con los datos ingresados en el formulario admin.
        """
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if isinstance(instance, Perfil):
                perfil_existente = Perfil.objects.filter(usuario=form.instance).first()
                if perfil_existente:
                    instance.pk = perfil_existente.pk
                    instance._state.adding = False
            instance.save()
        formset.save_m2m()


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol', 'especialidad', 'rut', 'telefono', 'registro_salud')
    list_filter = ('rol', 'especialidad')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'rut')


# Re-registrar UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Identidad Corporativa exigida por Módulo 2 (Criterio 2.1.2)
admin.site.site_header = 'Clínica CheckDent - Panel de Control'
admin.site.site_title = 'CheckDent Admin'
admin.site.index_title = 'Gestión Operativa de Recursos y Servicios'

# Restricción exclusiva: solo el Administrador Clínico (superuser o rol administrador) accede a Django Admin
def admin_exclusivo_has_permission(request):
    if not request.user.is_active or not request.user.is_authenticated:
        return False
    if request.user.is_superuser:
        return True
    if hasattr(request.user, 'perfil') and request.user.perfil.rol == 'administrador':
        return True
    return False

admin.site.has_permission = admin_exclusivo_has_permission
