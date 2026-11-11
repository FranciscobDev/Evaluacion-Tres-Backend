from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    """
    Extensión del modelo de usuario estándar de Django para gestionar
    roles del personal clínico (Odontólogos, Recepcionistas y Administradores).
    Los pacientes NO tienen cuenta de usuario; son gestionados por recepción.
    """
    ROL_CHOICES = [
        ('dentista', 'Dentista / Odontólogo'),
        ('recepcionista', 'Recepcionista'),
        ('administrador', 'Administrador de Clínica'),
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
        verbose_name="Funcionario"
    )
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='recepcionista',
        verbose_name="Rol en la Clínica"
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
        verbose_name = "Perfil de Funcionario"
        verbose_name_plural = "Perfiles de Funcionarios"

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
    """Crea automáticamente un perfil de funcionario si no existe al crear un nuevo User."""
    if created:
        rol = 'administrador' if instance.is_superuser else 'recepcionista'
        Perfil.objects.get_or_create(usuario=instance, defaults={'rol': rol})
    else:
        if hasattr(instance, 'perfil'):
            instance.perfil.save()
