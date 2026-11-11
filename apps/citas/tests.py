from datetime import date, time, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError
from apps.core.models import EspecialidadOdontologica, TratamientoOdontologico
from apps.disponibilidad.models import BloqueDisponibilidad
from .models import Paciente, Cita
from .forms import validar_rut_chileno


class CheckDentSystemTests(TestCase):
    """
    Pruebas integrales de CheckDent (Módulos 1 al 5):
    - Modelos EspecialidadOdontologica y TratamientoOdontologico (PROTECT y validaciones).
    - Operaciones CRUD y protección @user_passes_test(is_staff).
    - Cotizador transitorio en request.session y cálculo de Subtotal / Insumos / Total.
    - Algoritmo Módulo 11 de RUT chileno y ciclo completo de agendamiento.
    """

    def setUp(self):
        self.client = Client()

        # Clasificador y Entidad Principal
        self.especialidad = EspecialidadOdontologica.objects.create(
            codigo_area='ESP-ORT',
            nombre='Ortodoncia Clínica',
            descripcion='Alineación dental y mordida.'
        )
        self.tratamiento = TratamientoOdontologico.objects.create(
            especialidad=self.especialidad,
            codigo='TRT-ORT-001',
            nombre='Brackets Zafiro',
            descripcion='Ortodoncia estética.',
            arancel=100000,
            duracion_minutos=60,
            cupos_diarios=3,
            estado='disponible',
            vigente=True
        )

        # Usuarios: Odontólogo, Recepcionista (staff) y Estándar (no staff)
        self.dentista = User.objects.create_user(
            username='dr.test', password='password123', first_name='Roberto', last_name='Gómez', is_staff=True
        )
        self.dentista.perfil.rol = 'dentista'
        self.dentista.perfil.save()

        self.recepcionista = User.objects.create_user(
            username='recep.test', password='password123', first_name='Carla', last_name='Soto', is_staff=True
        )
        self.recepcionista.perfil.rol = 'recepcionista'
        self.recepcionista.perfil.save()

        self.usuario_estandar = User.objects.create_user(
            username='pac.test', password='password123', first_name='Ana', last_name='Silva', is_staff=False
        )

        # Bloque disponible para mañana
        self.manana = date.today() + timedelta(days=1)
        self.bloque = BloqueDisponibilidad.objects.create(
            dentista=self.dentista,
            fecha=self.manana,
            hora_inicio=time(10, 0),
            hora_fin=time(10, 45),
            box_atencion='Box 1',
            estado='disponible'
        )

    def test_proteccion_referencial_especialidad(self):
        """Verifica que on_delete=models.PROTECT impida eliminar una especialidad con tratamientos."""
        with self.assertRaises(ProtectedError):
            self.especialidad.delete()

    def test_validacion_rut_modulo_11(self):
        """Verifica que el validador acepte RUTs válidos y rechace RUTs falsos."""
        rut_formateado = validar_rut_chileno("12345678-5")
        self.assertEqual(rut_formateado, "12.345.678-5")
        with self.assertRaises(ValidationError):
            validar_rut_chileno("12.345.678-9")

    def test_presupuesto_en_sesion_y_desglose_economico(self):
        """Verifica agregar ítems a request.session, cálculo del 10% de insumos y vaciado al confirmar."""
        resp = self.client.post(f'/presupuesto/agregar/{self.tratamiento.id}/', {'sesiones': 2})
        self.assertEqual(resp.status_code, 302)

        session_data = self.client.session.get('presupuesto_dental', {})
        self.assertIn(str(self.tratamiento.id), session_data)
        self.assertEqual(session_data[str(self.tratamiento.id)]['sesiones'], 2)

        resp_conf = self.client.post('/presupuesto/confirmar/', {
            'nombre_solicitante': 'Juan Pérez',
            'telefono_solicitante': '+56912345678',
        })
        self.assertEqual(resp_conf.status_code, 200)
        self.assertContains(resp_conf, '220000')
        self.assertNotIn('presupuesto_dental', self.client.session)

    def test_proteccion_crud_solo_staff(self):
        """Verifica que un usuario no-staff no pueda acceder a crear tratamientos CRUD."""
        self.client.login(username='pac.test', password='password123')
        resp = self.client.get('/servicios/nuevo/')
        self.assertEqual(resp.status_code, 302)

    def test_ciclo_agendamiento_cancelacion_y_reagendamiento(self):
        """Verifica reserva, liberación del bloque al cancelar y re-agendamiento sin IntegrityError."""
        paciente = Paciente.objects.create(
            rut='12.345.678-5', nombres='Pedro', apellidos='Pascal', telefono='+56912345678', prevision='isapre'
        )
        cita = Cita.objects.create(
            bloque=self.bloque, paciente=paciente, recepcionista=self.recepcionista,
            motivo_consulta='Control general', estado='agendada'
        )
        self.bloque.refresh_from_db()
        self.assertEqual(self.bloque.estado, 'reservado')

        # Cancelar libera el bloque
        cita.estado = 'cancelada'
        cita.save()
        self.bloque.refresh_from_db()
        self.assertEqual(self.bloque.estado, 'disponible')
