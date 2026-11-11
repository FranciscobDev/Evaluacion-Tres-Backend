from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class BloqueDisponibilidad(models.Model):
    """
    Representa una franja horaria publicada por un dentista para atención de pacientes.
    """
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('reservado', 'Reservado'),
        ('cancelado', 'Cancelado'),
    ]

    dentista = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bloques_disponibles',
        verbose_name="Odontólogo Responsable"
    )
    fecha = models.DateField(
        verbose_name="Fecha de Atención"
    )
    hora_inicio = models.TimeField(
        verbose_name="Hora de Inicio"
    )
    hora_fin = models.TimeField(
        verbose_name="Hora de Término"
    )
    box_atencion = models.CharField(
        max_length=50,
        default="Box 1",
        verbose_name="Sillón / Box Dental"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='disponible',
        verbose_name="Estado de la Hora"
    )
    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Publicación"
    )

    class Meta:
        verbose_name = "Bloque de Disponibilidad"
        verbose_name_plural = "Bloques de Disponibilidad"
        ordering = ['fecha', 'hora_inicio']
        constraints = [
            models.UniqueConstraint(
                fields=['dentista', 'fecha', 'hora_inicio'],
                name='unique_bloque_dentista_horario'
            )
        ]

    def clean(self):
        # Validación de coherencia horaria
        if self.hora_inicio and self.hora_fin:
            if self.hora_inicio >= self.hora_fin:
                raise ValidationError("La hora de inicio debe ser anterior a la hora de término.")

    def __str__(self):
        nombre_dentista = self.dentista.get_full_name() or self.dentista.username
        hora_i = self.hora_inicio.strftime('%H:%M')
        hora_f = self.hora_fin.strftime('%H:%M')
        fecha_str = self.fecha.strftime('%d/%m/%Y')
        return f"{fecha_str} {hora_i} - {hora_f} | Dr(a). {nombre_dentista} ({self.get_estado_display()})"

    @property
    def esta_disponible(self):
        return self.estado == 'disponible'
