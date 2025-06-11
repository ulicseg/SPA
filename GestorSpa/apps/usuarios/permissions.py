from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def tiene_rol(roles_permitidos):
    """
    Decorador para verificar si el usuario tiene uno de los roles permitidos
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not hasattr(request.user, 'perfil'):
                messages.error(request, 'Tu perfil no está configurado correctamente.')
                return redirect('home')
            
            if request.user.perfil.rol in roles_permitidos or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'No tienes permisos para acceder a esta página.')
                return redirect('home')
        
        return _wrapped_view
    return decorator


def es_cliente(user):
    """Verifica si el usuario es cliente"""
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol == 'cliente'


def es_profesional(user):
    """Verifica si el usuario es profesional"""
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol == 'profesional'


def es_administrador(user):
    """Verifica si el usuario es administrador"""
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol == 'administrador'


def es_personal_autorizado(user):
    """Verifica si el usuario es profesional o administrador"""
    return user.is_authenticated and hasattr(user, 'perfil') and user.perfil.rol in ['profesional', 'administrador']


# Decoradores específicos
cliente_required = user_passes_test(es_cliente, login_url='login')
profesional_required = user_passes_test(es_profesional, login_url='login')
administrador_required = user_passes_test(es_administrador, login_url='login')
personal_autorizado_required = user_passes_test(es_personal_autorizado, login_url='login')


class ClienteRequiredMixin(UserPassesTestMixin):
    """Mixin para vistas que requieren rol de cliente"""
    
    def test_func(self):
        return es_cliente(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, 'Solo los clientes pueden acceder a esta página.')
        return redirect('home')


class ProfesionalRequiredMixin(UserPassesTestMixin):
    """Mixin para vistas que requieren rol de profesional"""
    
    def test_func(self):
        return es_profesional(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, 'Solo los profesionales pueden acceder a esta página.')
        return redirect('home')


class AdministradorRequiredMixin(UserPassesTestMixin):
    """Mixin para vistas que requieren rol de administrador"""
    
    def test_func(self):
        return es_administrador(self.request.user) or self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, 'Solo los administradores pueden acceder a esta página.')
        return redirect('home')


class PersonalAutorizadoRequiredMixin(UserPassesTestMixin):
    """Mixin para vistas que requieren rol de profesional o administrador"""
    
    def test_func(self):
        return es_personal_autorizado(self.request.user) or self.request.user.is_superuser
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')


def verificar_permiso_turno(user, turno):
    """
    Verifica si un usuario puede ver/editar un turno específico
    """
    if user.is_superuser:
        return True
    
    if not hasattr(user, 'perfil'):
        return False
    
    perfil = user.perfil
    
    # Los administradores pueden ver todos los turnos
    if perfil.rol == 'administrador':
        return True
    
    # Los profesionales pueden ver turnos donde están asignados (si implementas asignación)
    if perfil.rol == 'profesional':
        return True  # Por ahora todos los profesionales pueden ver todos los turnos
    
    # Los clientes solo pueden ver sus propios turnos
    if perfil.rol == 'cliente':
        return turno.email == user.email
    
    return False
