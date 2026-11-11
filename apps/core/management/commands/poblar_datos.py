from datetime import date, time, timedelta
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

        # 2. Entidades Principales Gestionables (10 Tratamientos Odontológicos)
        tratamientos_data = [
            ("TRT-ORT-001", "ESP-ORT", "Instalación de Brackets Metálicos",
             "Cementado de arco completo de brackets de autoligado con control biomecánico inicial.",
             "Requiere radiografía panorámica y telerradiografía lateral.", 180000, 60, 4, "disponible"),
            ("TRT-ORT-002", "ESP-ORT", "Alineadores Invisibles Transparentes",
             "Set inicial de férulas termoplásticas personalizadas tras escaneo intraoral 3D.",
             "Higiene dental previa sin presencia de caries activas.", 320000, 45, 3, "en_curso"),
            ("TRT-END-001", "ESP-END", "Endodoncia Unirradicular Mecanizada",
             "Desinfección rotatoria y obturación termoplástica de conducto en incisivos o caninos.",
             "Radiografía retroalveolar periapical previa.", 95000, 60, 5, "disponible"),
            ("TRT-END-002", "ESP-END", "Endodoncia Multirradicular de Molar",
             "Tratamiento de conducto de alta complejidad con localizador apical electrónico en molares.",
             "Evaluación de restaurabilidad coronaria previa.", 145000, 90, 3, "disponible"),
            ("TRT-PER-001", "ESP-PER", "Destartraje Supragingival y Profilaxis",
             "Limpieza dental por ultrasonido para remoción de tártaro, placa bacteriana y manchas.",
             "No requiere preparación especial previa.", 38000, 45, 8, "disponible"),
            ("TRT-PER-002", "ESP-PER", "Pulido Radicular por Cuadrante",
             "Descontaminación subgingival profunda para el control de enfermedad periodontal activa.",
             "Periodontograma clínico previo.", 65000, 60, 5, "disponible"),
            ("TRT-IMP-001", "ESP-IMP", "Implante Dental de Titanio Grado IV",
             "Inserción quirúrgica de fijación oseointegrada de titanio para reemplazo de raíz dental.",
             "Tomografía Cone Beam (CBCT) del maxilar correspondiente.", 390000, 90, 2, "disponible"),
            ("TRT-IMP-002", "ESP-IMP", "Exodoncia de Tercer Molar (Muela del Juicio)",
             "Extracción quirúrgica atraumática de tercer molar semi-incluido bajo anestesia local.",
             "Radiografía panorámica vigente menor a 6 meses.", 85000, 60, 4, "en_curso"),
            ("TRT-PED-001", "ESP-PED", "Sellantes Fotopolimerizables + Fluoración",
             "Sellado preventivo de fosas y fisuras en molares definitivos jóvenes más barniz de flúor.",
             "Niños y adolescentes de 6 a 14 años.", 32000, 30, 10, "disponible"),
            ("TRT-EST-001", "ESP-EST", "Blanqueamiento Dental Clínico LED",
             "Aclaramiento dental fotoactivado con peróxido de hidrógeno de uso clínico y barrera gingival.",
             "Destartraje previo realizado en los últimos 30 días.", 110000, 60, 6, "disponible"),
        ]

        for cod, cod_esp, nom, desc, ind, aran, dur, cupos, est in tratamientos_data:
            TratamientoOdontologico.objects.update_or_create(
                codigo=cod,
                defaults={
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
            )
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

        dr_roberto, created = User.objects.get_or_create(username="dr.roberto", defaults={
            'first_name': "Roberto",
            'last_name': "Gómez",
            'email': "roberto.gomez@checkdent.cl",
            'is_staff': True,
        })
        if created:
            dr_roberto.set_password("dentista123")
            dr_roberto.save()
        dr_roberto.perfil.rol = "dentista"
        dr_roberto.perfil.especialidad = "ortodoncia"
        dr_roberto.perfil.telefono = "+56 9 2233 4455"
        dr_roberto.perfil.rut = "15.432.189-K"
        dr_roberto.perfil.registro_salud = "REG-MED-84920"
        dr_roberto.perfil.save()

        dra_camila, created = User.objects.get_or_create(username="dra.camila", defaults={
            'first_name': "Camila",
            'last_name': "Morales",
            'email': "camila.morales@checkdent.cl",
            'is_staff': True,
        })
        if created:
            dra_camila.set_password("dentista123")
            dra_camila.save()
        dra_camila.perfil.rol = "dentista"
        dra_camila.perfil.especialidad = "endodoncia"
        dra_camila.perfil.telefono = "+56 9 3344 5566"
        dra_camila.perfil.rut = "16.789.234-5"
        dra_camila.perfil.registro_salud = "REG-MED-91234"
        dra_camila.perfil.save()

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

        paciente_user, created = User.objects.get_or_create(username="paciente.demo", defaults={
            'first_name': "Valentina",
            'last_name': "Muñoz",
            'email': "valentina@correo.cl",
            'is_staff': False,
        })
        if created:
            paciente_user.set_password("paciente123")
            paciente_user.save()
        paciente_user.perfil.rol = "paciente"
        paciente_user.perfil.rut = "12.345.678-5"
        paciente_user.perfil.telefono = "+56 9 9988 7766"
        paciente_user.perfil.save()
        self.stdout.write(self.style.SUCCESS("✓ Cuentas de prueba (admin, dentistas, recepción y usuario estándar) listas."))

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
            for dentista, box in [(dr_roberto, "Box 1 - Ortodoncia"), (dra_camila, "Box 2 - Endodoncia")]:
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
            dentista=dr_roberto, fecha=hoy, estado='disponible'
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

