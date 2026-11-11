import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('disponibilidad', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Paciente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rut', models.CharField(max_length=12, unique=True, verbose_name='RUT / Identificación')),
                ('nombres', models.CharField(max_length=100, verbose_name='Nombres')),
                ('apellidos', models.CharField(max_length=100, verbose_name='Apellidos')),
                ('telefono', models.CharField(max_length=20, verbose_name='Teléfono / WhatsApp')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Correo Electrónico')),
                ('fecha_nacimiento', models.DateField(blank=True, null=True, verbose_name='Fecha de Nacimiento')),
                ('prevision', models.CharField(choices=[('particular', 'Particular'), ('fonasa', 'Fonasa'), ('isapre', 'Isapre'), ('convenio', 'Convenio Empresa')], default='particular', max_length=20, verbose_name='Previsión de Salud')),
                ('alergias_antecedentes', models.TextField(blank=True, verbose_name='Alergias o Antecedentes Clínicos Relevantes')),
                ('creado_en', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')),
            ],
            options={
                'verbose_name': 'Paciente',
                'verbose_name_plural': 'Pacientes',
                'ordering': ['apellidos', 'nombres'],
            },
        ),
        migrations.CreateModel(
            name='Cita',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('motivo_consulta', models.TextField(help_text='Ej: Dolor dental, limpieza, evaluación de ortodoncia, etc.', verbose_name='Motivo de la Consulta')),
                ('estado', models.CharField(choices=[('agendada', 'Agendada'), ('confirmada', 'Confirmada'), ('en_atencion', 'En Atención'), ('realizada', 'Realizada / Atendida'), ('cancelada', 'Cancelada'), ('no_asistio', 'No Asistió')], default='agendada', max_length=20, verbose_name='Estado de la Cita')),
                ('notas_clinicas', models.TextField(blank=True, help_text='Observaciones o indicaciones dejadas por el dentista tras la sesión.', verbose_name='Notas del Odontólogo')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Agendamiento')),
                ('fecha_actualizacion', models.DateTimeField(auto_now=True, verbose_name='Última Actualización')),
                ('bloque', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='cita', to='disponibilidad.bloquedisponibilidad', verbose_name='Bloque de Hora Asignado')),
                ('recepcionista', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='citas_agendadas', to=settings.AUTH_USER_MODEL, verbose_name='Recepcionista Responsable')),
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='citas', to='citas.paciente', verbose_name='Paciente')),
            ],
            options={
                'verbose_name': 'Cita Odontológica',
                'verbose_name_plural': 'Citas Odontológicas',
                'ordering': ['bloque__fecha', 'bloque__hora_inicio'],
            },
        ),
    ]
