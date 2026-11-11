from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from .models import BloqueDisponibilidad
from .forms import BloqueIndividualForm, GenerarJornadaForm
from apps.citas.models import Cita


@login_required
def mi_agenda(request):
    """
    Vista principal del Odontólogo:
    Visualiza su agenda de pacientes asignados por recepción y sus bloques disponibles.
    """
    if not hasattr(request.user, 'perfil') or not request.user.perfil.es_dentista:
        messages.warning(request, "Esta sección es exclusiva para el cuerpo de Odontólogos.")
        return redirect('usuarios:perfil')

    citas = Cita.objects.filter(
        bloque__dentista=request.user
    ).select_related('bloque', 'paciente', 'recepcionista').order_by('bloque__fecha', 'bloque__hora_inicio')

    bloques_libres = BloqueDisponibilidad.objects.filter(
        dentista=request.user,
        estado='disponible'
    ).order_by('fecha', 'hora_inicio')

    return render(request, 'disponibilidad/mi_agenda.html', {
        'citas': citas,
        'bloques_libres': bloques_libres,
    })


@login_required
def publicar_bloque(request):
    """
    Permite al odontólogo publicar disponibilidad:
    1. Bloque único.
    2. Generación automática por jornada (intervalos periódicos).
    """
    if not hasattr(request.user, 'perfil') or not request.user.perfil.es_dentista:
        messages.warning(request, "Solo los odontólogos pueden publicar horas de atención.")
        return redirect('usuarios:perfil')

    form_individual = BloqueIndividualForm(prefix='ind')
    form_jornada = GenerarJornadaForm(prefix='jor')

    if request.method == 'POST':
        tipo_accion = request.POST.get('tipo_accion')

        if tipo_accion == 'individual':
            form_individual = BloqueIndividualForm(request.POST, prefix='ind')
            if form_individual.is_valid():
                bloque = form_individual.save(commit=False)
                bloque.dentista = request.user
                bloque.estado = 'disponible'
                try:
                    bloque.save()
                    messages.success(
                        request,
                        f"✓ Bloque publicado con éxito para el {bloque.fecha.strftime('%d/%m/%Y')} de {bloque.hora_inicio.strftime('%H:%M')} a {bloque.hora_fin.strftime('%H:%M')}."
                    )
                    return redirect('disponibilidad:mi_agenda')
                except IntegrityError:
                    messages.error(request, "Ya tienes un bloque registrado para esa misma fecha y hora de inicio.")

        elif tipo_accion == 'jornada':
            form_jornada = GenerarJornadaForm(request.POST, prefix='jor')
            if form_jornada.is_valid():
                fecha = form_jornada.cleaned_data['fecha']
                h_ini = form_jornada.cleaned_data['hora_inicio_jornada']
                h_fin = form_jornada.cleaned_data['hora_fin_jornada']
                duracion = timedelta(minutes=form_jornada.cleaned_data['duracion_bloque'])
                box = form_jornada.cleaned_data['box_atencion']

                # Combinar fecha y hora para iterar
                cursor_actual = datetime.combine(fecha, h_ini)
                limite_jornada = datetime.combine(fecha, h_fin)

                bloques_creados = 0
                bloques_omitidos = 0

                while cursor_actual + duracion <= limite_jornada:
                    inicio_slot = cursor_actual.time()
                    fin_slot = (cursor_actual + duracion).time()

                    # Verificar si ya existe este bloque para no duplicar
                    existe = BloqueDisponibilidad.objects.filter(
                        dentista=request.user,
                        fecha=fecha,
                        hora_inicio=inicio_slot
                    ).exists()

                    if not existe:
                        BloqueDisponibilidad.objects.create(
                            dentista=request.user,
                            fecha=fecha,
                            hora_inicio=inicio_slot,
                            hora_fin=fin_slot,
                            box_atencion=box,
                            estado='disponible'
                        )
                        bloques_creados += 1
                    else:
                        bloques_omitidos += 1

                    cursor_actual += duracion

                if bloques_creados > 0:
                    msg = f"✓ Se generaron {bloques_creados} bloques horarios para el día {fecha.strftime('%d/%m/%Y')}."
                    if bloques_omitidos > 0:
                        msg += f" ({bloques_omitidos} omitidos porque ya existían)."
                    messages.success(request, msg)
                    return redirect('disponibilidad:mi_agenda')
                else:
                    messages.warning(request, "No se crearon nuevos bloques (todos los horarios calculados ya estaban registrados).")

    return render(request, 'disponibilidad/publicar_bloque.html', {
        'form_individual': form_individual,
        'form_jornada': form_jornada,
    })


@login_required
def eliminar_bloque(request, id):
    """
    Permite al dentista retirar un bloque libre que aún no haya sido asignado a ningún paciente.
    """
    if not hasattr(request.user, 'perfil') or not request.user.perfil.es_dentista:
        return redirect('usuarios:perfil')

    bloque = get_object_or_404(BloqueDisponibilidad, id=id, dentista=request.user)

    if bloque.estado != 'disponible':
        messages.error(request, "No puedes eliminar una hora que ya está reservada o asignada a un paciente.")
        return redirect('disponibilidad:mi_agenda')

    if request.method == 'POST':
        fecha_str = bloque.fecha.strftime('%d/%m/%Y')
        hora_str = bloque.hora_inicio.strftime('%H:%M')
        bloque.delete()
        messages.success(request, f"Bloque libre del {fecha_str} a las {hora_str} retirado de la parrilla.")
        return redirect('disponibilidad:mi_agenda')

    return redirect('disponibilidad:mi_agenda')


@login_required
def actualizar_nota_clinica(request, id):
    """
    Permite al odontólogo registrar o actualizar notas clínicas de una cita ya asignada.
    """
    if not hasattr(request.user, 'perfil') or not request.user.perfil.es_dentista:
        return redirect('usuarios:perfil')

    cita = get_object_or_404(Cita, id=id, bloque__dentista=request.user)

    if request.method == 'POST':
        notas = request.POST.get('notas_clinicas', '').strip()
        cita.notas_clinicas = notas
        cita.save(update_fields=['notas_clinicas', 'fecha_actualizacion'])
        messages.success(request, f"Notas clínicas actualizadas para el paciente {cita.paciente.nombre_completo}.")

    return redirect('disponibilidad:mi_agenda')
