from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import LoginForm, RegistroUsuarioForm


def es_administrador(user):
    """Verifica que el usuario sea Administrador de la clínica."""
    return user.is_authenticated and (
        user.is_superuser or (hasattr(user, 'perfil') and user.perfil.rol == 'administrador')
    )


@login_required
@user_passes_test(es_administrador)
def registro_usuario(request):
    """Permite exclusivamente al Administrador registrar nuevo personal clínico."""
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            nuevo_user = form.save()
            messages.success(
                request,
                f"✓ Funcionario {nuevo_user.get_full_name()} ({nuevo_user.perfil.get_rol_display()}) registrado con éxito."
            )
            return redirect('core:inicio')
        else:
            messages.error(request, "Por favor corrige los errores señalados en el formulario.")
    else:
        form = RegistroUsuarioForm()

    return render(request, 'usuarios/registro.html', {'form': form})


def login_usuario(request):
    """Gestiona el inicio de sesión exclusivo de dentistas, recepcionistas y administradores."""
    if request.user.is_authenticated:
        return redirect('usuarios:redireccion_rol')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            rol_nombre = user.perfil.get_rol_display() if hasattr(user, 'perfil') else "Funcionario"
            messages.success(
                request,
                f"¡Bienvenido(a), {user.get_full_name() or user.username}! Sesión iniciada como {rol_nombre}."
            )
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('usuarios:redireccion_rol')
        else:
            messages.error(request, "Usuario o contraseña incorrectos. Verifica tus credenciales institucionales.")
    else:
        form = LoginForm()

    return render(request, 'usuarios/login.html', {
        'form': form,
        'next': request.GET.get('next', '')
    })


def logout_usuario(request):
    """Cierra la sesión del funcionario actual."""
    logout(request)
    messages.info(request, "Has cerrado tu sesión clínica correctamente. ¡Hasta pronto!")
    return redirect('core:inicio')


@login_required
def redireccion_rol(request):
    """
    Redirige al funcionario a su panel operativo según su rol:
    - Dentista -> su agenda de pacientes y publicación de horas
    - Recepcionista / Administrador -> panel de recepción y agendamiento
    """
    if hasattr(request.user, 'perfil'):
        if request.user.perfil.es_dentista:
            return redirect('disponibilidad:mi_agenda')
        if request.user.perfil.es_recepcionista:
            return redirect('citas:panel_recepcion')
    return redirect('core:inicio')


@login_required
def perfil_usuario(request):
    """Muestra la ficha institucional del funcionario conectado."""
    return render(request, 'usuarios/perfil.html', {'usuario': request.user})
