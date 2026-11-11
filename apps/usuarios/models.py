from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    """
    Extensión del modelo de usuario estándar de Django para gestionar
    roles institucionales, RUT y datos profesionales dentro de CheckDent.
    """
    ROL_CHOICES = [
        ('dentista', 'Dentista / Odontólogo'),
        ('recepcionista', 'Recepcionista'),
        ('administrador', 'Administrador de Clínica'),
        ('paciente', 'Paciente / Usuario Estándar'),
    ]

    ESPECIALIDADES = [
        ('general', 'Odontología General'),
        ('ortodoncia', 'Ortodoncia'),
        ('endodoncia', 'Endodoncia'),
        ('periodoncia', 'Periodoncia'),
        ('odontopediatria', 'Odontopediatría'),
        ('cirugia', 'Cirugía Maxilofacial e Implantes'),
        ('rehabilitacion', 'Rehabilitación Oral y Estética'),
    ]

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
        verbose_name="Usuario"
    )
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='paciente',
        verbose_name="Rol Institucional"
    )
    rut = models.CharField(
        max_length=12,
        blank=True,
        verbose_name="RUT / Identificación"
    )
    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono de Contacto"
    )

    # Datos específicos para Odontólogos
    especialidad = models.CharField(
        max_length=30,
        choices=ESPECIALIDADES,
        blank=True,
        default='general',
        verbose_name="Especialidad Odontológica"
    )
    registro_salud = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="N° Registro Superintendencia de Salud"
    )

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"

    def __str__(self):
        nombre = self.usuario.get_full_name() or self.usuario.username
        return f"{nombre} ({self.get_rol_display()})"

    @property
    def es_dentista(self):
        return self.rol == 'dentista'

    @property
    def es_recepcionista(self):
        return self.rol in ['recepcionista', 'administrador']


@receiver(post_save, sender=User)
def crear_o_actualizar_perfil(sender, instance, created, **kwargs):
    """Crea automáticamente un perfil básico si se crea un nuevo User."""
    if created:
        rol = 'administrador' if instance.is_superuser else 'paciente'
        Perfil.objects.create(usuario=instance, rol=rol)
    else:
        if hasattr(instance, 'perfil'):
            instance.perfil.save()
