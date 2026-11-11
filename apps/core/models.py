from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class EspecialidadOdontologica(models.Model):
    """
    Entidad de Contexto / Agrupación (Módulo 1 - Criterio 2.1.1):
    Representa la disciplina o área clínica odontológica a la que pertenecen los tratamientos.
    """
    codigo_area = models.CharField(
        max_length=15,
        unique=True,
        verbose_name="Código de Área",
        help_text="Ej: ESP-ORT, ESP-END, ESP-IMP"
    )
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Nombre de la Especialidad"
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        verbose_name="Slug URL"
    )
    descripcion = models.TextField(
        verbose_name="Descripción Clínica del Área"
    )
    icono = models.CharField(
        max_length=50,
        default="bi-shield-plus",
        verbose_name="Icono Bootstrap (bi-*)"
    )
    activa = models.BooleanField(
        default=True,
        verbose_name="Área Activa"
    )

    class Meta:
        verbose_name = "Especialidad Odontológica"
        verbose_name_plural = "Especialidades Odontológicas"
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        self.codigo_area = self.codigo_area.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.codigo_area})"


class TratamientoOdontologico(models.Model):
    """
    Entidad Principal Gestionable (Módulo 1 - Criterio 2.1.1):
    Representa una prestación, servicio o procedimiento odontológico del catálogo clínico.
    """
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('en_curso', 'En Curso / Alta Demanda'),
        ('suspendido', 'Suspendido Temporalmente'),
    ]

    especialidad = models.ForeignKey(
        EspecialidadOdontologica,
        on_delete=models.PROTECT,
        related_name='tratamientos',
        verbose_name="Especialidad Odontológica"
    )
    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código Único de Prestación",
        help_text="Identificador alfanumérico único (ej. TRT-ORT-001)"
    )
    slug = models.SlugField(
        max_length=160,
        unique=True,
        blank=True,
        verbose_name="Identificador URL (Slug)"
    )
    nombre = models.CharField(
        max_length=140,
        verbose_name="Nombre del Tratamiento"
    )
    descripcion = models.TextField(
        verbose_name="Descripción Clínica y Procedimiento"
    )
    indicaciones_previas = models.CharField(
        max_length=255,
        blank=True,
        default="Evaluación diagnóstica inicial y radiografía panorámica según indicación.",
        verbose_name="Requisitos / Indicaciones para el Paciente"
    )
    arancel = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Arancel Clínico ($ CLP)",
        help_text="Valor en pesos chilenos por sesión o prestación."
    )
    duracion_minutos = models.PositiveIntegerField(
        default=45,
        validators=[MinValueValidator(15)],
        verbose_name="Duración Estimada (minutos)"
    )
    cupos_diarios = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(0)],
        verbose_name="Cupos Diarios Disponibles"
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='disponible',
        verbose_name="Estado Operativo"
    )
    imagen = models.ImageField(
        upload_to='tratamientos/',
        blank=True,
        null=True,
        verbose_name="Imagen / Fotografía Clínica"
    )
    vigente = models.BooleanField(
        default=True,
        verbose_name="Vigente (Control de Baja Lógica)"
    )
    creado_en = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Registro"
    )
    actualizado_en = models.DateTimeField(
        auto_now=True,
        verbose_name="Última Modificación"
    )

    class Meta:
        verbose_name = "Tratamiento Odontológico"
        verbose_name_plural = "Tratamientos Odontológicos"
        ordering = ['especialidad__nombre', 'nombre']

    def save(self, *args, **kwargs):
        self.codigo = self.codigo.strip().upper()
        if not self.slug:
            base_slug = slugify(f"{self.codigo}-{self.nombre}")
            self.slug = base_slug[:160]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.codigo}] {self.nombre} (${self.arancel:,})"

    @property
    def puede_cotizarse(self):
        return self.vigente and self.estado != 'suspendido' and self.cupos_diarios > 0


