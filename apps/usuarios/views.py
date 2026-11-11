from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegistroUsuarioForm


def registro_usuario(request):
    """Permite registrar una nueva cuenta de usuario con su Perfil asociado."""
    if request.user.is_authenticated:
        return redirect('usuarios:redireccion_rol')

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"¡Cuenta creada con éxito! Bienvenido(a) a Clínica CheckDent, {user.get_full_name()}."
            )
            return redirect('core:servicios')
        else:
            messages.error(request, "Por favor corrige los errores señalados en el formulario de registro.")
    else:
        form = RegistroUsuarioForm()

    return render(request, 'usuarios/registro.html', {'form': form})


def login_usuario(request):
    """Gestiona el inicio de sesión de dentistas, recepcionistas, administradores y pacientes."""
    if request.user.is_authenticated:
        return redirect('usuarios:redireccion_rol')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            rol_nombre = user.perfil.get_rol_display() if hasattr(user, 'perfil') else "Usuario"
            messages.success(
                request,
                f"¡Bienvenido(a), {user.get_full_name() or user.username}! Sesión iniciada como {rol_nombre}."
            )
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('usuarios:redireccion_rol')
        else:
            messages.error(request, "Usuario o contraseña incorrectos. Verifica tus credenciales.")
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {
        'form': form,
        'next': request.GET.get('next', '')
    })


def logout_usuario(request):
    """Cierra la sesión del usuario actual."""
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente. ¡Hasta pronto!")
    return redirect('core:inicio')


@login_required
def redireccion_rol(request):
    """
    Redirige al usuario a su panel correspondiente según su rol:
    - Dentista -> su agenda de pacientes
    - Recepcionista / Administrador -> panel de recepción
    - Paciente / Usuario estándar -> catálogo de tratamientos
    """
    if hasattr(request.user, 'perfil'):
        if request.user.perfil.es_dentista:
            return redirect('disponibilidad:mi_agenda')
        if request.user.perfil.es_recepcionista:
            return redirect('citas:panel_recepcion')
    return redirect('core:servicios')


@login_required
def perfil_usuario(request):
    """Muestra los datos y rol institucional del usuario conectado."""
    return render(request, 'usuarios/perfil.html', {'usuario': request.user})
