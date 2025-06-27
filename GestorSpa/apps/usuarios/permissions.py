from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.apps import apps
from django.db import transaction


class RoleManager:
    """Gestor de roles y permisos del sistema"""
      # Definición de roles
    ROLES = {
        'cliente': {
            'name': 'cliente',
            'description': 'Puede reservar turnos y ver su historial',
            'permissions': [
                'turnos.add_turno',
                'turnos.view_turno',
            ]
        },
        'profesional': {
            'name': 'profesional',
            'description': 'Puede consultar turnos asignados y ver detalles',
            'permissions': [
                'turnos.view_turno',
                'turnos.change_turno',
                'servicios.view_servicio',
            ]
        },
        'administrador': {
            'name': 'administrador',
            'description': 'Puede gestionar turnos y servicios (CRUD completo)',
            'permissions': [
                'turnos.add_turno',
                'turnos.change_turno',
                'turnos.delete_turno',
                'turnos.view_turno',
                'servicios.add_servicio',
                'servicios.change_servicio',
                'servicios.delete_servicio',
                'servicios.view_servicio',
                'usuarios.view_perfil',
                'usuarios.change_perfil',
            ]
        }
    }

    @classmethod
    def create_groups_and_permissions(cls):
        """Crea los grupos y asigna permisos correspondientes"""
        
        with transaction.atomic():
            for role_key, role_data in cls.ROLES.items():
                # Crear o obtener el grupo
                group, created = Group.objects.get_or_create(
                    name=role_data['name']
                )
                
                if created:
                    print(f"Grupo creado: {role_data['name']}")
                else:
                    print(f"Grupo ya existe: {role_data['name']}")
                
                # Limpiar permisos existentes del grupo
                group.permissions.clear()
                
                # Asignar permisos al grupo
                for perm_code in role_data['permissions']:
                    try:
                        app_label, codename = perm_code.split('.')
                        permission = Permission.objects.get(
                            content_type__app_label=app_label,
                            codename=codename
                        )
                        group.permissions.add(permission)
                        print(f"  Permiso asignado: {perm_code}")
                    except Permission.DoesNotExist:
                        print(f"  ADVERTENCIA: Permiso no encontrado: {perm_code}")
                    except ValueError:
                        print(f"  ERROR: Formato de permiso inválido: {perm_code}")

    @classmethod
    def assign_role_to_user(cls, user, role_key):
        """Asigna un rol específico a un usuario"""
        if role_key not in cls.ROLES:
            raise ValueError(f"Rol '{role_key}' no existe")
        
        # Remover de todos los grupos de roles
        for role_data in cls.ROLES.values():
            try:
                group = Group.objects.get(name=role_data['name'])
                user.groups.remove(group)
            except Group.DoesNotExist:
                pass
        
        # Asignar al nuevo grupo
        group = Group.objects.get(name=cls.ROLES[role_key]['name'])
        user.groups.add(group)
        
        print(f"Usuario {user.username} asignado al rol: {cls.ROLES[role_key]['name']}")

    @classmethod
    def get_user_role(cls, user):
        """Obtiene el rol actual del usuario"""
        for role_key, role_data in cls.ROLES.items():
            try:
                group = Group.objects.get(name=role_data['name'])
                if user.groups.filter(id=group.id).exists():
                    return role_key
            except Group.DoesNotExist:
                pass
        return None

    @classmethod
    def user_has_role(cls, user, role_key):
        """Verifica si un usuario tiene un rol específico"""
        if role_key not in cls.ROLES:
            return False
        
        try:
            group = Group.objects.get(name=cls.ROLES[role_key]['name'])
            return user.groups.filter(id=group.id).exists()
        except Group.DoesNotExist:
            return False

    @classmethod
    def get_available_roles(cls):
        """Retorna los roles disponibles para asignación"""
        return [(key, data['name']) for key, data in cls.ROLES.items()]


# Decoradores personalizados para permisos
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps


def role_required(*roles):
    """
    Decorador que requiere que el usuario tenga uno de los roles especificados
    Uso: @role_required('cliente', 'administrador')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied("Debe estar autenticado")
            
            user_role = RoleManager.get_user_role(request.user)
            if user_role not in roles:
                raise PermissionDenied(f"Acceso denegado. Roles requeridos: {', '.join(roles)}")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def cliente_required(view_func):
    """Decorador específico para clientes"""
    return role_required('cliente')(view_func)


def profesional_required(view_func):
    """Decorador específico para profesionales"""
    return role_required('profesional')(view_func)


def administrador_required(view_func):
    """Decorador específico para administradores"""
    return role_required('administrador')(view_func)


def cliente_or_admin_required(view_func):
    """Decorador para clientes o administradores"""
    return role_required('cliente', 'administrador')(view_func)


def profesional_or_admin_required(view_func):
    """Decorador para profesionales o administradores"""
    return role_required('profesional', 'administrador')(view_func)


# Mixin para vistas basadas en clases
from django.contrib.auth.mixins import UserPassesTestMixin


class RoleRequiredMixin(UserPassesTestMixin):
    """Mixin para requerir roles específicos en vistas basadas en clases"""
    required_roles = []
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        user_role = RoleManager.get_user_role(self.request.user)
        return user_role in self.required_roles


class ClienteRequiredMixin(RoleRequiredMixin):
    required_roles = ['cliente']


class ProfesionalRequiredMixin(RoleRequiredMixin):
    required_roles = ['profesional']


class AdministradorRequiredMixin(RoleRequiredMixin):
    required_roles = ['administrador']


class ClienteOrAdminRequiredMixin(RoleRequiredMixin):
    required_roles = ['cliente', 'administrador']


class ProfesionalOrAdminRequiredMixin(RoleRequiredMixin):
    required_roles = ['profesional', 'administrador']
