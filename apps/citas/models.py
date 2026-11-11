from django.db import models
from django.contrib.auth.models import User
from apps.disponibilidad.models import BloqueDisponibilidad


class Paciente(models.Model):
    """
    Representa al cliente o paciente de la clínica.
    NO tiene cuenta de acceso al sistema; es registrado y gestionado por la recepción.
    """
    PREVISION_CHOICES = [
        ('particular', 'Particular'),
        ('fonasa', 'Fonasa'),
        ('isapre', 'Isapre'),
        ('convenio', 'Convenio Empresa'),
    ]

    rut = models.CharField(
        max_length=12,
        unique=True,
        verbose_name="RUT / Identificación"
    )
    nombres = models.CharField(
        max_length=100,
        verbose_name="Nombres"
    )
    apellidos = models.CharField(
        max_length=100,
        verbose_name="Apellidos"
    )
    telefono = models.CharField(
        max_length=20,
        verbose_name="Teléfono / WhatsApp"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Correo Electrónico"
    )
    fecha_nacimiento = models.DateField(
        blank=True,
        null=True,
        verbose_name="Fecha de Nacimiento"
    )
    prevision = models.CharField(
        max_length=20,
        choices=PREVISION_CHOICES,
        default='particular',
        verbose_name="Previsión de Salud"
    )
    alergias_antecedentes = models.TextField(
        blank=True,
        verbose_name="Alergias o Antecedentes Clínicos Relevantes"
    )
    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Registro"
    )

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.apellidos}, {self.nombres} ({self.rut})"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


class Cita(models.Model):
    """
    Vincula un Bloque de Disponibilidad con un Paciente, asignado por un Recepcionista.
    """
    ESTADO_CITA_CHOICES = [
        ('agendada', 'Agendada'),
        ('confirmada', 'Confirmada'),
        ('en_atencion', 'En Atención'),
        ('realizada', 'Realizada / Atendida'),
        ('cancelada', 'Cancelada'),
        ('no_asistio', 'No Asistió'),
    ]

    bloque = models.OneToOneField(
        BloqueDisponibilidad,
        on_delete=models.PROTECT,
        related_name='cita',
        verbose_name="Bloque de Hora Asignado"
    )
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.PROTECT,
        related_name='citas',
        verbose_name="Paciente"
    )
    recepcionista = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='citas_agendadas',
        verbose_name="Recepcionista Responsable"
    )
    motivo_consulta = models.TextField(
        verbose_name="Motivo de la Consulta",
        help_text="Ej: Dolor dental, limpieza, evaluación de ortodoncia, etc."
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CITA_CHOICES,
        default='agendada',
        verbose_name="Estado de la Cita"
    )
    notas_clinicas = models.TextField(
        blank=True,
        verbose_name="Notas del Odontólogo",
        help_text="Observaciones o indicaciones dejadas por el dentista tras la sesión."
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Agendamiento"
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Actualización"
    )

    class Meta:
        verbose_name = "Cita Odontológica"
        verbose_name_plural = "Citas Odontológicas"
        ordering = ['bloque__fecha', 'bloque__hora_inicio']

    def __str__(self):
        fecha = self.bloque.fecha.strftime('%d/%m/%Y')
        hora = self.bloque.hora_inicio.strftime('%H:%M')
        return f"Cita {self.paciente.nombre_completo} - {fecha} {hora} ({self.get_estado_display()})"

    def save(self, *args, **kwargs):
        # Al agendar una cita activa, el bloque horario pasa a 'reservado'
        if self.estado in ['agendada', 'confirmada', 'en_atencion', 'realizada']:
            if self.bloque.estado != 'reservado':
                self.bloque.estado = 'reservado'
                self.bloque.save(update_fields=['estado'])
        elif self.estado == 'cancelada':
            # Si se cancela la cita, el bloque vuelve a quedar 'disponible'
            if self.bloque.estado != 'disponible':
                self.bloque.estado = 'disponible'
                self.bloque.save(update_fields=['estado'])
        super().save(*args, **kwargs)
