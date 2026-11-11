from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import EspecialidadOdontologica, TratamientoOdontologico
from .forms import TratamientoOdontologicoForm
from apps.disponibilidad.models import BloqueDisponibilidad
from apps.citas.models import Cita


def es_personal_staff(user):
    """Verifica que el usuario sea miembro del staff clínico/administrativo."""
    return user.is_authenticated and user.is_staff


def inicio(request):
    """Portada principal institucional de la clínica CheckDent."""
    total_dentistas = User.objects.filter(perfil__rol='dentista').count()
    horas_disponibles = BloqueDisponibilidad.objects.filter(estado='disponible').count()
    citas_hoy = Cita.objects.count()
    total_tratamientos = TratamientoOdontologico.objects.filter(vigente=True).count()

    dentistas = User.objects.filter(perfil__rol='dentista').select_related('perfil')
    tratamientos_destacados = TratamientoOdontologico.objects.filter(
        vigente=True, estado='disponible'
    ).select_related('especialidad')[:3]

    return render(request, 'core/index.html', {
        'total_dentistas': total_dentistas,
        'horas_disponibles': horas_disponibles,
        'citas_hoy': citas_hoy,
        'total_tratamientos': total_tratamientos,
        'dentistas': dentistas,
        'tratamientos_destacados': tratamientos_destacados,
    })


# ==============================================================================
# OPERACIONES CRUD EN FRONTEND (CRITERIO 2.1.3)
# ==============================================================================

def servicios(request):
    """
    Operación R (Read - Catálogo):
    Buscador multi-campo con objeto Q (nombre, código y descripción),
    filtro por EspecialidadOdontologica, ordenamiento y paginación con Paginator.
    """
    query = request.GET.get('q', '').strip()
    especialidad_id = request.GET.get('especialidad', '').strip()
    orden = request.GET.get('orden', 'nombre').strip()

    tratamientos_qs = TratamientoOdontologico.objects.filter(
        vigente=True
    ).select_related('especialidad')

    # Búsqueda simultánea multi-campo con objeto Q
    if query:
        tratamientos_qs = tratamientos_qs.filter(
            Q(nombre__icontains=query) |
            Q(codigo__icontains=query) |
            Q(descripcion__icontains=query)
        )

    # Filtro por entidad de contexto (EspecialidadOdontologica)
    especialidad_actual_id = int(especialidad_id) if especialidad_id.isdigit() else None
    if especialidad_actual_id:
        tratamientos_qs = tratamientos_qs.filter(especialidad_id=especialidad_actual_id)

    # Ordenamiento seguro
    ordenes_validos = {
        'nombre': 'nombre',
        'arancel_asc': 'arancel',
        'arancel_desc': '-arancel',
    }
    tratamientos_qs = tratamientos_qs.order_by(ordenes_validos.get(orden, 'nombre'))

    # Paginator (6 por página: con 5 servicios todos se muestran en una sola página sin barra extra)
    paginator = Paginator(tratamientos_qs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    especialidades = EspecialidadOdontologica.objects.filter(activa=True)

    return render(request, 'core/servicios.html', {
        'page_obj': page_obj,
        'tratamientos': page_obj,
        'especialidades': especialidades,
        'query': query,
        'especialidad_actual': especialidad_actual_id,
        'orden_actual': orden,
    })


def detalle_tratamiento(request, slug):
    """
    Operación R (Read - Detalle):
    Ficha individual del tratamiento odontológico accesible mediante su slug.
    """
    tratamiento = get_object_or_404(
        TratamientoOdontologico.objects.select_related('especialidad'),
        slug=slug
    )
    return render(request, 'core/detalle_tratamiento.html', {
        'tratamiento': tratamiento,
    })


@login_required
@user_passes_test(es_personal_staff)
def crear_tratamiento(request):
    """
    Operación C (Create):
    Creación de un nuevo tratamiento odontológico con soporte de archivos (request.FILES).
    """
    if request.method == 'POST':
        form = TratamientoOdontologicoForm(request.POST, request.FILES)
        if form.is_valid():
            tratamiento = form.save()
            messages.success(
                request,
                f"✓ Tratamiento '{tratamiento.nombre}' ({tratamiento.codigo}) registrado exitosamente."
            )
            return redirect('core:detalle_tratamiento', slug=tratamiento.slug)
        else:
            messages.error(request, "Revisa los campos del formulario antes de guardar.")
    else:
        form = TratamientoOdontologicoForm()

    return render(request, 'core/tratamiento_form.html', {
        'form': form,
        'titulo_pagina': 'Registrar Nuevo Tratamiento Odontológico',
        'modo_edicion': False,
    })


@login_required
@user_passes_test(es_personal_staff)
def editar_tratamiento(request, slug):
    """
    Operación U (Update):
    Modificación de un tratamiento existente con formulario precargado.
    """
    tratamiento = get_object_or_404(TratamientoOdontologico, slug=slug)

    if request.method == 'POST':
        form = TratamientoOdontologicoForm(request.POST, request.FILES, instance=tratamiento)
        if form.is_valid():
            tratamiento = form.save()
            messages.success(
                request,
                f"✓ Tratamiento '{tratamiento.nombre}' actualizado correctamente."
            )
            return redirect('core:detalle_tratamiento', slug=tratamiento.slug)
        else:
            messages.error(request, "No se pudo actualizar el tratamiento. Verifica los errores.")
    else:
        form = TratamientoOdontologicoForm(instance=tratamiento)

    return render(request, 'core/tratamiento_form.html', {
        'form': form,
        'tratamiento': tratamiento,
        'titulo_pagina': f"Editar Tratamiento: {tratamiento.codigo}",
        'modo_edicion': True,
    })


@login_required
@user_passes_test(es_personal_staff)
def eliminar_tratamiento(request, slug):
    """
    Operación D (Delete):
    Eliminación controlada con pantalla de confirmación previa (soporta baja lógica o borrado físico).
    """
    tratamiento = get_object_or_404(TratamientoOdontologico, slug=slug)

    if request.method == 'POST':
        tipo_baja = request.POST.get('tipo_baja', 'logica')
        nombre = tratamiento.nombre
        codigo = tratamiento.codigo

        if tipo_baja == 'fisica':
            tratamiento.delete()
            messages.warning(
                request,
                f"El tratamiento '{nombre}' ({codigo}) fue eliminado permanentemente de la base de datos."
            )
        else:
            tratamiento.vigente = False
            tratamiento.estado = 'suspendido'
            tratamiento.save(update_fields=['vigente', 'estado', 'actualizado_en'])
            messages.info(
                request,
                f"Se aplicó baja lógica al tratamiento '{nombre}' ({codigo}). Ya no aparece en el catálogo público."
            )
        return redirect('core:servicios')

    return render(request, 'core/confirmar_eliminacion.html', {'tratamiento': tratamiento})


# ==============================================================================
# COLECCIÓN EN SESIÓN HTTP (CRITERIO 2.1.4)
# ==============================================================================

def _calcular_resumen_presupuesto(presupuesto_dict):
    """Calcula ítems, subtotal, recargo de insumos de bioseguridad (10%) y total final."""
    items = []
    subtotal = 0
    for key, data in presupuesto_dict.items():
        arancel = int(data.get('arancel', 0))
        sesiones = int(data.get('sesiones', 1))
        total_linea = arancel * sesiones
        subtotal += total_linea
        items.append({
            'id': key,
            'codigo': data.get('codigo'),
            'nombre': data.get('nombre'),
            'especialidad': data.get('especialidad'),
            'slug': data.get('slug'),
            'arancel': arancel,
            'sesiones': sesiones,
            'cupos_max': int(data.get('cupos_max', 5)),
            'total_linea': total_linea,
        })
    insumos_esterilizacion = int(round(subtotal * 0.10))
    total_final = subtotal + insumos_esterilizacion
    return {
        'items_presupuesto': items,
        'subtotal': subtotal,
        'insumos_esterilizacion': insumos_esterilizacion,
        'total_final': total_final,
    }


def agregar_al_presupuesto(request, tratamiento_id):
    """Agrega un tratamiento al presupuesto en request.session validando disponibilidad y cupos."""
    tratamiento = get_object_or_404(
        TratamientoOdontologico.objects.select_related('especialidad'),
        id=tratamiento_id
    )

    if not tratamiento.vigente or tratamiento.estado == 'suspendido' or tratamiento.cupos_diarios <= 0:
        messages.error(
            request,
            f"El tratamiento '{tratamiento.nombre}' no tiene cupos disponibles o se encuentra suspendido."
        )
        return redirect('core:servicios')

    presupuesto = request.session.get('presupuesto_dental', {})
    key = str(tratamiento.id)
    sesiones_solicitadas = int(request.POST.get('sesiones', 1)) if request.method == 'POST' else 1
    if sesiones_solicitadas < 1:
        sesiones_solicitadas = 1

    sesiones_actuales = presupuesto.get(key, {}).get('sesiones', 0)
    nueva_cantidad = sesiones_actuales + sesiones_solicitadas

    if nueva_cantidad > tratamiento.cupos_diarios:
        messages.warning(
            request,
            f"Solo existen {tratamiento.cupos_diarios} cupos diarios para '{tratamiento.nombre}'. Se ajustó al máximo permitido."
        )
        nueva_cantidad = tratamiento.cupos_diarios

    presupuesto[key] = {
        'codigo': tratamiento.codigo,
        'nombre': tratamiento.nombre,
        'especialidad': tratamiento.especialidad.nombre,
        'slug': tratamiento.slug,
        'arancel': tratamiento.arancel,
        'sesiones': nueva_cantidad,
        'cupos_max': tratamiento.cupos_diarios,
    }

    request.session['presupuesto_dental'] = presupuesto
    request.session.modified = True
    messages.success(
        request,
        f"✓ '{tratamiento.nombre}' agregado al Cotizador ({nueva_cantidad} sesión/piezas)."
    )
    return redirect('core:ver_presupuesto')


def actualizar_item_presupuesto(request, tratamiento_id):
    """Modifica la cantidad de sesiones/piezas de un tratamiento en la sesión."""
    if request.method == 'POST':
        presupuesto = request.session.get('presupuesto_dental', {})
        key = str(tratamiento_id)

        if key in presupuesto:
            tratamiento = TratamientoOdontologico.objects.filter(id=tratamiento_id).first()
            cupos_max = tratamiento.cupos_diarios if tratamiento else presupuesto[key].get('cupos_max', 5)
            try:
                nuevas_sesiones = int(request.POST.get('sesiones', 1))
            except ValueError:
                nuevas_sesiones = 1

            if nuevas_sesiones <= 0:
                nombre_elim = presupuesto[key]['nombre']
                del presupuesto[key]
                messages.info(request, f"Se retiró '{nombre_elim}' del cotizador.")
            else:
                if nuevas_sesiones > cupos_max:
                    nuevas_sesiones = cupos_max
                    messages.warning(request, f"Cantidad ajustada al límite de {cupos_max} cupos disponibles.")
                else:
                    messages.success(request, f"Cantidad actualizada para '{presupuesto[key]['nombre']}'.")
                presupuesto[key]['sesiones'] = nuevas_sesiones

            request.session['presupuesto_dental'] = presupuesto
            request.session.modified = True

    return redirect('core:ver_presupuesto')


def eliminar_item_presupuesto(request, tratamiento_id):
    """Elimina un tratamiento individual de request.session."""
    presupuesto = request.session.get('presupuesto_dental', {})
    key = str(tratamiento_id)
    if key in presupuesto:
        nombre = presupuesto[key]['nombre']
        del presupuesto[key]
        request.session['presupuesto_dental'] = presupuesto
        request.session.modified = True
        messages.info(request, f"Tratamiento '{nombre}' eliminado del cotizador.")
    return redirect('core:ver_presupuesto')


def vaciar_presupuesto(request):
    """Vacía completamente la colección transitoria en request.session."""
    if 'presupuesto_dental' in request.session:
        del request.session['presupuesto_dental']
        request.session.modified = True
    messages.info(request, "El cotizador en sesión ha sido vaciado.")
    return redirect('core:ver_presupuesto')


def ver_presupuesto(request):
    """Muestra el detalle del presupuesto acumulado en sesión con desglose financiero."""
    presupuesto = request.session.get('presupuesto_dental', {})
    contexto = _calcular_resumen_presupuesto(presupuesto)
    return render(request, 'core/presupuesto.html', contexto)


def confirmar_solicitud_presupuesto(request):
    """
    Procesa la solicitud del presupuesto dental, vacía request.session y
    emite un comprobante clínico imprimible con folio único.
    """
    presupuesto = request.session.get('presupuesto_dental', {})
    if not presupuesto:
        messages.warning(request, "El cotizador está vacío. Agrega al menos un tratamiento antes de confirmar.")
        return redirect('core:servicios')

    if request.method == 'POST':
        resumen = _calcular_resumen_presupuesto(presupuesto)
        nombre_solicitante = request.POST.get('nombre_solicitante', '').strip() or 'Paciente Clínico'
        telefono_solicitante = request.POST.get('telefono_solicitante', '').strip() or '+56 9 0000 0000'

        del request.session['presupuesto_dental']
        request.session.modified = True

        folio = f"PRES-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        messages.success(
            request,
            f"✓ Comprobante #{folio} emitido correctamente. La sesión ha sido vaciada."
        )
        return render(request, 'core/comprobante_presupuesto.html', {
            **resumen,
            'folio': folio,
            'fecha_emision': datetime.now(),
            'nombre_solicitante': nombre_solicitante,
            'telefono_solicitante': telefono_solicitante,
        })

    return redirect('core:ver_presupuesto')


def contacto(request):
    """Página institucional de ubicación, horarios y canales de contacto."""
    return render(request, 'core/contacto.html')
