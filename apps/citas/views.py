from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.db.models import Q
from apps.disponibilidad.models import BloqueDisponibilidad
from .models import Paciente, Cita
from .forms import AgendarCitaForm


@login_required
def panel_recepcion(request):
    """
    Panel de operaciones del recepcionista:
    1. Visualiza las horas disponibles publicadas por los dentistas (con filtros).
    2. Gestiona las citas ya agendadas y permite cambiar sus estados en tiempo real.
    """
    if not hasattr(request.user, 'perfil') or not request.user.perfil.es_recepcionista:
        messages.warning(request, "Acceso restringido al personal de Recepción y Administración.")
        return redirect('usuarios:perfil')

    # Filtros de búsqueda para horas disponibles
    dentista_id = request.GET.get('dentista', '')
    fecha_filtro = request.GET.get('fecha', '')
    query_paciente = request.GET.get('q_paciente', '').strip()

    bloques_libres = BloqueDisponibilidad.objects.filter(
        estado='disponible'
    ).select_related('dentista', 'dentista__perfil').order_by('fecha', 'hora_inicio')

    if dentista_id:
        bloques_libres = bloques_libres.filter(dentista_id=dentista_id)

    if fecha_filtro:
        bloques_libres = bloques_libres.filter(fecha=fecha_filtro)

    # Citas agendadas en el sistema
    citas = Cita.objects.select_related(
        'bloque', 'bloque__dentista', 'bloque__dentista__perfil', 'paciente', 'recepcionista'
    ).order_by('bloque__fecha', 'bloque__hora_inicio')

    if query_paciente:
        citas = citas.filter(
            Q(paciente__nombres__icontains=query_paciente) |
            Q(paciente__apellidos__icontains=query_paciente) |
            Q(paciente__rut__icontains=query_paciente) |
            Q(paciente__telefono__icontains=query_paciente)
        )

    dentistas = User.objects.filter(perfil__rol='dentista').select_related('perfil')

    return render(request, 'citas/panel_recepcion.html', {
        'bloques_disponibles': bloques_libres,
        'citas': citas,
        'dentistas': dentistas,
        'dentista_id_actual': dentista_id,
        'fecha_actual': fecha_filtro,
        'query_paciente': query_paciente,
        'total_disponibles': bloques_libres.count(),
        'total_citas': citas.count(),
    })


@login_required
def agendar_cita(request, bloque_id):
    """
    Asigna un bloque libre a un paciente. Si el paciente ya existe por su RUT,
    lo reutiliza y actualiza sus datos; si es nuevo, lo crea en el sistema.
    """
    if not hasattr(request.user, 'perfil') or not request.user.perfil.es_recepcionista:
        messages.warning(request, "Solo el personal de recepción puede agendar pacientes.")
        return redirect('usuarios:perfil')

    bloque = get_object_or_404(
        BloqueDisponibilidad.objects.select_related('dentista', 'dentista__perfil'),
        id=bloque_id
    )

    # Validar que el bloque siga libre
    if bloque.estado != 'disponible':
        messages.error(request, "Este horario ya fue reservado o retirado de la parrilla.")
        return redirect('citas:panel_recepcion')

    if request.method == 'POST':
        form = AgendarCitaForm(request.POST)
        if form.is_valid():
            rut = form.cleaned_data['rut']

            # Buscar o crear/actualizar al paciente por RUT
            paciente, _ = Paciente.objects.update_or_create(
                rut=rut,
                defaults={
                    'nombres': form.cleaned_data['nombres'],
                    'apellidos': form.cleaned_data['apellidos'],
                    'telefono': form.cleaned_data['telefono'],
                    'email': form.cleaned_data.get('email') or None,
                    'prevision': form.cleaned_data['prevision'],
                    'alergias_antecedentes': form.cleaned_data.get('alergias_antecedentes', ''),
                }
            )

            # Crear o reactivar la cita sobre el bloque disponible (permite re-agendar horas canceladas)
            cita, _ = Cita.objects.update_or_create(
                bloque=bloque,
                defaults={
                    'paciente': paciente,
                    'recepcionista': request.user,
                    'motivo_consulta': form.cleaned_data['motivo_consulta'],
                    'estado': 'agendada',
                    'notas_clinicas': '',
                }
            )

            messages.success(
                request,
                f"✓ Cita confirmada con éxito para el paciente {paciente.nombre_completo} "
                f"con Dr(a). {bloque.dentista.get_full_name() or bloque.dentista.username} "
                f"el {bloque.fecha.strftime('%d/%m/%Y')} a las {bloque.hora_inicio.strftime('%H:%M')}."
            )
            return redirect('citas:detalle_cita', cita_id=cita.id)
    else:
        rut_param = request.GET.get('rut', '').strip()
        initial_data = {}
        if rut_param:
            paciente_existente = Paciente.objects.filter(rut=rut_param).first()
            if paciente_existente:
                initial_data = {
                    'rut': paciente_existente.rut,
                    'nombres': paciente_existente.nombres,
                    'apellidos': paciente_existente.apellidos,
                    'telefono': paciente_existente.telefono,
                    'email': paciente_existente.email,
                    'prevision': paciente_existente.prevision,
                    'alergias_antecedentes': paciente_existente.alergias_antecedentes,
                }
            else:
                initial_data['rut'] = rut_param
        form = AgendarCitaForm(initial=initial_data)

    return render(request, 'citas/agendar_cita.html', {
        'bloque': bloque,
        'form': form,
    })


@login_required
def detalle_cita(request, cita_id):
    """
    Muestra la ficha y comprobante completo de una cita odontológica agendada.
    """
    cita = get_object_or_404(
        Cita.objects.select_related(
            'bloque', 'bloque__dentista', 'bloque__dentista__perfil', 'paciente', 'recepcionista'
        ),
        id=cita_id
    )
    return render(request, 'citas/detalle_cita.html', {'cita': cita})


@login_required
def cambiar_estado_cita(request, cita_id):
    """
    Permite a la recepcionista cambiar el estado de la cita.
    Si se marca como 'cancelada', el bloque horario vuelve a quedar libre en la parrilla.
    """
    if not hasattr(request.user, 'perfil') or not request.user.perfil.es_recepcionista:
        return redirect('usuarios:perfil')

    cita = get_object_or_404(Cita.objects.select_related('bloque', 'paciente'), id=cita_id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('nuevo_estado')
        estados_validos = dict(Cita.ESTADO_CITA_CHOICES)

        if nuevo_estado in estados_validos:
            cita.estado = nuevo_estado
            cita.save()

            if nuevo_estado == 'cancelada':
                messages.warning(
                    request,
                    f"Cita cancelada. El horario del {cita.bloque.fecha.strftime('%d/%m/%Y')} a las "
                    f"{cita.bloque.hora_inicio.strftime('%H:%M')} ha quedado nuevamente disponible en parrilla."
                )
            else:
                messages.success(
                    request,
                    f"Estado de la cita para {cita.paciente.nombre_completo} actualizado a '{estados_validos[nuevo_estado]}'."
                )

    return redirect('citas:panel_recepcion')


@login_required
def buscar_paciente_api(request):
    """
    Endpoint JSON ligero para autocompletar datos del paciente en el formulario
    cuando la recepcionista escribe el RUT.
    """
    rut = request.GET.get('rut', '').strip().upper()
    paciente = Paciente.objects.filter(rut=rut).first()

    if paciente:
        return JsonResponse({
            'encontrado': True,
            'rut': paciente.rut,
            'nombres': paciente.nombres,
            'apellidos': paciente.apellidos,
            'telefono': paciente.telefono,
            'email': paciente.email or '',
            'prevision': paciente.prevision,
            'alergias': paciente.alergias_antecedentes,
        })
    return JsonResponse({'encontrado': False})
