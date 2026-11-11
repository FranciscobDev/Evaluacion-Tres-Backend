import os
from datetime import date, time, timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.models import EspecialidadOdontologica, TratamientoOdontologico
from apps.disponibilidad.models import BloqueDisponibilidad
from apps.citas.models import Paciente, Cita


class Command(BaseCommand):
    help = "Pobla la base de datos de CheckDent con 6 especialidades, 10 tratamientos, usuarios y agenda."

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando sembrado integral de datos en Clínica CheckDent...")

        # 1. Clasificadores / Entidades de Contexto (6 Especialidades Odontológicas)
        especialidades_data = [
            ("ESP-ORT", "Ortodoncia y Ortopedia", "bi-braces",
             "Corrección de la alineación dental y mordida con brackets metálicos, zafiro y alineadores invisibles."),
            ("ESP-END", "Endodoncia Clínica", "bi-activity",
             "Alivio del dolor pulpar y conservación de piezas dentales mediante tratamiento de conducto mecanizado."),
            ("ESP-PER", "Periodoncia e Higiene", "bi-shield-check",
             "Prevención, diagnóstico y tratamiento de enfermedades de las encías y tejidos de soporte dental."),
            ("ESP-IMP", "Implantología y Cirugía", "bi-hospital",
             "Cirugía de terceros molares y rehabilitación fija mediante implantes oseointegrados de titanio."),
            ("ESP-PED", "Odontopediatría", "bi-emoji-smile",
             "Atención odontológica preventiva y restauradora especializada para niños y adolescentes."),
            ("ESP-EST", "Rehabilitación y Estética", "bi-stars",
             "Diseño digital de sonrisa, blanqueamiento clínico LED, carillas y coronas libres de metal."),
        ]

        mapa_esp = {}
        for codigo, nombre, icono, desc in especialidades_data:
            esp, _ = EspecialidadOdontologica.objects.update_or_create(
                codigo_area=codigo,
                defaults={
                    'nombre': nombre,
                    'icono': icono,
                    'descripcion': desc,
                    'activa': True,
                }
            )
            mapa_esp[codigo] = esp
        self.stdout.write(self.style.SUCCESS(f"✓ {len(mapa_esp)} Especialidades Odontológicas (clasificadores) cargadas."))

        # 2. Entidades Principales Gestionables (5 Tratamientos Odontológicos)
        tratamientos_data = [
            ("TRT-ORT-001", "ESP-ORT", "Instalación de Brackets Metálicos",
             "Cementado de arco completo de brackets de autoligado con control biomecánico inicial.",
             "Requiere radiografía panorámica y telerradiografía lateral.", 180000, 60, 4, "disponible"),
            ("TRT-END-001", "ESP-END", "Endodoncia Unirradicular Mecanizada",
             "Desinfección rotatoria y obturación termoplástica de conducto en incisivos o caninos.",
             "Radiografía retroalveolar periapical previa.", 95000, 60, 5, "disponible"),
            ("TRT-PER-001", "ESP-PER", "Destartraje Supragingival y Profilaxis",
             "Limpieza dental por ultrasonido para remoción de tártaro, placa bacteriana y manchas.",
             "No requiere preparación especial previa.", 38000, 45, 8, "disponible"),
            ("TRT-IMP-001", "ESP-IMP", "Implante Dental de Titanio Grado IV",
             "Inserción quirúrgica de fijación oseointegrada de titanio para reemplazo de raíz dental.",
             "Tomografía Cone Beam (CBCT) del maxilar correspondiente.", 390000, 90, 2, "disponible"),
            ("TRT-EST-001", "ESP-EST", "Blanqueamiento Dental Clínico LED",
             "Aclaramiento dental fotoactivado con peróxido de hidrógeno de uso clínico y barrera gingival.",
             "Destartraje previo realizado en los últimos 30 días.", 110000, 60, 6, "disponible"),
        ]

        codigos_mantener = [t[0] for t in tratamientos_data]
        TratamientoOdontologico.objects.exclude(codigo__in=codigos_mantener).delete()

        for cod, cod_esp, nom, desc, ind, aran, dur, cupos, est in tratamientos_data:
            img_rel = f"tratamientos/{nom}.png"
            img_full = os.path.join(settings.MEDIA_ROOT, img_rel)
            defaults_dict = {
                'especialidad': mapa_esp[cod_esp],
                'nombre': nom,
                'descripcion': desc,
                'indicaciones_previas': ind,
                'arancel': aran,
                'duracion_minutos': dur,
                'cupos_diarios': cupos,
                'estado': est,
                'vigente': True,
            }
            if os.path.exists(img_full):
                defaults_dict['imagen'] = img_rel

            trat, _ = TratamientoOdontologico.objects.update_or_create(
                codigo=cod,
                defaults=defaults_dict
            )
            if os.path.exists(img_full) and not trat.imagen:
                trat.imagen = img_rel
                trat.save()
        self.stdout.write(self.style.SUCCESS(f"✓ {len(tratamientos_data)} Tratamientos Odontológicos cargados."))

        # 3. Usuarios de Prueba (Admin, Dentistas, Recepcionista y Usuario Estándar)
        if not User.objects.filter(username="admin").exists():
            admin_user = User.objects.create_superuser("admin", "admin@checkdent.cl", "admin123")
            admin_user.first_name = "Administrador"
            admin_user.last_name = "General"
            admin_user.save()
        else:
            admin_user = User.objects.get(username="admin")
        admin_user.perfil.rol = "administrador"
        admin_user.perfil.rut = "10.111.222-3"
        admin_user.perfil.telefono = "+56 9 1111 2222"
        admin_user.perfil.save()

        dr_mauricio, created = User.objects.get_or_create(username="dr.mauricio", defaults={
            'first_name': "Mauricio",
            'last_name': "López",
            'email': "mauricio.lopez@checkdent.cl",
            'is_staff': True,
        })
        if created:
            dr_mauricio.set_password("dentista123")
            dr_mauricio.save()
        dr_mauricio.first_name = "Mauricio"
        dr_mauricio.last_name = "López"
        dr_mauricio.save()
        dr_mauricio.perfil.rol = "dentista"
        dr_mauricio.perfil.especialidad = "ortodoncia"
        dr_mauricio.perfil.telefono = "+56 9 2233 4455"
        dr_mauricio.perfil.rut = "15.432.189-K"
        dr_mauricio.perfil.registro_salud = "REG-MED-84920"
        dr_mauricio.perfil.save()

        dr_ismael, created = User.objects.get_or_create(username="dr.ismael", defaults={
            'first_name': "Ismael",
            'last_name': "Figueroa",
            'email': "ismael.figueroa@checkdent.cl",
            'is_staff': True,
        })
        if created:
            dr_ismael.set_password("dentista123")
            dr_ismael.save()
        dr_ismael.first_name = "Ismael"
        dr_ismael.last_name = "Figueroa"
        dr_ismael.save()
        dr_ismael.perfil.rol = "dentista"
        dr_ismael.perfil.especialidad = "endodoncia"
        dr_ismael.perfil.telefono = "+56 9 3344 5566"
        dr_ismael.perfil.rut = "16.789.234-5"
        dr_ismael.perfil.registro_salud = "REG-MED-91234"
        dr_ismael.perfil.save()

        dr_francisco, created = User.objects.get_or_create(username="dr.francisco", defaults={
            'first_name': "Francisco",
            'last_name': "Miranda",
            'email': "francisco.miranda@checkdent.cl",
            'is_staff': True,
        })
        if created:
            dr_francisco.set_password("dentista123")
            dr_francisco.save()
        dr_francisco.first_name = "Francisco"
        dr_francisco.last_name = "Miranda"
        dr_francisco.save()
        dr_francisco.perfil.rol = "dentista"
        dr_francisco.perfil.especialidad = "odontopediatria"
        dr_francisco.perfil.telefono = "+56 9 5566 7788"
        dr_francisco.perfil.rut = "17.890.123-4"
        dr_francisco.perfil.registro_salud = "REG-MED-77123"
        dr_francisco.perfil.save()

        recep_carla, created = User.objects.get_or_create(username="carla.recepcion", defaults={
            'first_name': "Carla",
            'last_name': "Soto",
            'email': "recepcion@checkdent.cl",
            'is_staff': True,
        })
        if created:
            recep_carla.set_password("recepcion123")
            recep_carla.save()
        recep_carla.perfil.rol = "recepcionista"
        recep_carla.perfil.telefono = "+56 9 4455 6677"
        recep_carla.perfil.rut = "18.321.654-2"
        recep_carla.perfil.save()

        # Eliminar cuenta paciente.demo si existía previamente (los pacientes no tienen login)
        User.objects.filter(username="paciente.demo").delete()
        self.stdout.write(self.style.SUCCESS("✓ Cuentas de personal clínico (admin, dentistas y recepción) listas."))

        # 4. Pacientes de Recepción (RUTs válidos Módulo 11)
        pacientes_data = [
            ("12.345.678-5", "Juan Carlos", "Pérez Díaz", "+56 9 8765 4321", "juan.perez@email.com", "fonasa"),
            ("11.111.111-1", "María José", "López Castro", "+56 9 7654 3210", "maria.lopez@email.com", "isapre"),
            ("22.222.222-2", "Andrés", "Vargas Silva", "+56 9 6543 2109", "andres.vargas@email.com", "particular"),
        ]
        pacientes_creados = []
        for rut, nom, ape, tel, email, prev in pacientes_data:
            pac, _ = Paciente.objects.get_or_create(
                rut=rut,
                defaults={
                    'nombres': nom,
                    'apellidos': ape,
                    'telefono': tel,
                    'email': email,
                    'prevision': prev,
                }
            )
            pacientes_creados.append(pac)

        # 5. Bloques de Disponibilidad para los próximos 3 días
        hoy = date.today()
        horarios = [
            (time(9, 0), time(9, 45)),
            (time(10, 0), time(10, 45)),
            (time(11, 0), time(11, 45)),
            (time(15, 0), time(15, 45)),
            (time(16, 0), time(16, 45)),
        ]
        for offset in range(3):
            dia = hoy + timedelta(days=offset)
            for dentista, box in [
                (dr_mauricio, "Box 1 - Ortodoncia"),
                (dr_ismael, "Box 2 - Endodoncia"),
                (dr_francisco, "Box 3 - Odontopediatría")
            ]:
                for h_ini, h_fin in horarios:
                    BloqueDisponibilidad.objects.get_or_create(
                        dentista=dentista,
                        fecha=dia,
                        hora_inicio=h_ini,
                        defaults={
                            'hora_fin': h_fin,
                            'box_atencion': box,
                            'estado': 'disponible'
                        }
                    )

        # 6. Cita de ejemplo agendada para hoy
        bloque_ejemplo = BloqueDisponibilidad.objects.filter(
            dentista=dr_mauricio, fecha=hoy, estado='disponible'
        ).first()
        if bloque_ejemplo:
            Cita.objects.get_or_create(
                bloque=bloque_ejemplo,
                defaults={
                    'paciente': pacientes_creados[0],
                    'recepcionista': recep_carla,
                    'motivo_consulta': "Control de frenillos / ajuste de brackets mensuales.",
                    'estado': 'agendada'
                }
            )

        self.stdout.write(self.style.SUCCESS("\n¡Base de datos de CheckDent poblada exitosamente con poblar_datos!"))

