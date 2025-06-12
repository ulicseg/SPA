# Sistema de Roles y Permisos - GestorSpa

## Descripción General

El sistema de roles implementado en GestorSpa permite gestionar diferentes tipos de usuarios con permisos específicos según su función en el spa.

## Roles Implementados

### 👤 Cliente
**Descripción:** Usuarios que reservan y utilizan los servicios del spa.

**Permisos:**
- ✅ Puede reservar turnos
- ✅ Ver su historial de turnos
- ✅ Editar su perfil personal
- ❌ No puede gestionar servicios
- ❌ No puede ver turnos de otros usuarios

**Funcionalidades:**
- Dashboard personalizado con sus turnos
- Formulario de reserva con datos pre-completados
- Vista de "Mis Turnos" con historial completo
- Perfil personal editable

### 👨‍⚕️ Profesional
**Descripción:** Personal del spa que brinda los servicios.

**Permisos:**
- ✅ Ver turnos asignados (próximos y del día)
- ✅ Cambiar estado de turnos
- ✅ Ver información de servicios
- ✅ Editar su perfil profesional
- ❌ No puede crear/eliminar servicios
- ❌ No puede gestionar usuarios

**Funcionalidades:**
- Dashboard con estadísticas de turnos
- Vista de turnos del día y próximos
- Información profesional en el perfil (licencia, especialidad)
- Acceso de solo lectura a servicios

### 👩‍💼 Administrador (Dra. Ana Felicidad)
**Descripción:** Gestión completa del sistema spa.

**Permisos:**
- ✅ CRUD completo de servicios
- ✅ CRUD completo de turnos
- ✅ Gestionar usuarios y roles
- ✅ Acceso al panel de administración
- ✅ Ver reportes y estadísticas
- ✅ Todas las funcionalidades del sistema

**Funcionalidades:**
- Dashboard completo con estadísticas generales
- Gestión de servicios (crear, editar, eliminar)
- Gestión de turnos (ver todos, editar, eliminar)
- Gestión de usuarios (asignar roles, crear usuarios)
- Acceso completo al admin de Django

## Implementación Técnica

### Estructura de Archivos

```
GestorSpa/apps/usuarios/
├── permissions.py          # Gestor de roles y decoradores
├── models.py              # Modelo Perfil extendido
├── admin.py              # Admin con gestión de roles
├── views.py              # Vistas con permisos por rol
├── management/commands/
│   ├── setup_roles.py     # Configurar grupos y permisos
│   └── create_demo_users.py # Crear usuarios demo
└── templates/usuarios/
    ├── perfil.html        # Dashboard por rol
    ├── gestionar_usuarios.html
    └── mis_turnos.html
```

### Grupos de Django

El sistema utiliza los grupos nativos de Django:
- **Cliente**: Permisos básicos de turnos
- **Profesional**: Permisos de consulta y cambio
- **Dr/a. Ana Felicidad (Administrador)**: Permisos completos

### Decoradores Disponibles

```python
# Decoradores para funciones
@cliente_required
@profesional_required  
@administrador_required
@role_required('cliente', 'administrador')

# Mixins para vistas basadas en clases
class ClienteRequiredMixin
class ProfesionalRequiredMixin
class AdministradorRequiredMixin
class ClienteOrAdminRequiredMixin
```

### Métodos de Verificación

```python
# En modelos
user.perfil.is_cliente()
user.perfil.is_profesional()  
user.perfil.is_administrador()

# En RoleManager
RoleManager.get_user_role(user)
RoleManager.user_has_role(user, 'cliente')
RoleManager.assign_role_to_user(user, 'administrador')
```

## Comandos de Gestión

### Configurar Roles Iniciales
```bash
python manage.py setup_roles --create-groups
```

### Listar Roles Disponibles
```bash
python manage.py setup_roles --list-roles
```

### Asignar Rol a Usuario
```bash
python manage.py setup_roles --assign-role username:cliente
```

### Crear Usuarios Demo
```bash
python manage.py create_demo_users
```

### Ver Roles de Usuarios
```bash
python manage.py setup_roles --show-user-roles
```

## Navegación por Rol

### Cliente
- Inicio
- Reservar Turno
- Mis Turnos
- Mi Perfil

### Profesional  
- Inicio
- Ver Turnos
- Ver Servicios
- Mi Perfil

### Administrador
- Inicio
- Administración (dropdown)
  - Gestionar Servicios
  - Gestionar Turnos
  - Gestionar Usuarios
  - Panel Admin
- Nuevo Turno
- Mi Perfil

## Seguridad

### Protección de Vistas
- Todas las vistas administrativas requieren autenticación
- Los decoradores verifican permisos antes de permitir acceso
- Los mixins protegen vistas basadas en clases
- Las URLs sensibles están protegidas por roles

### Validaciones
- Los clientes solo ven sus propios turnos
- Los profesionales no pueden eliminar servicios
- Solo administradores pueden gestionar usuarios
- Verificación de permisos en templates

## Personalización del Dashboard

Cada rol tiene un dashboard personalizado:

### Cliente
- Últimos turnos personales
- Servicios disponibles
- Acceso rápido a reservar

### Profesional
- Estadísticas de turnos
- Turnos del día
- Turnos pendientes

### Administrador
- Estadísticas generales
- Acciones rápidas
- Últimos turnos del sistema
- Gestión completa

## Extensión del Sistema

Para agregar nuevos roles:

1. **Definir en `permissions.py`:**
```python
ROLES = {
    'nuevo_rol': {
        'name': 'Nombre del Rol',
        'description': 'Descripción del rol',
        'permissions': ['app.permission_name']
    }
}
```

2. **Crear decorador:**
```python
def nuevo_rol_required(view_func):
    return role_required('nuevo_rol')(view_func)
```

3. **Añadir mixin:**
```python
class NuevoRolRequiredMixin(RoleRequiredMixin):
    required_roles = ['nuevo_rol']
```

4. **Actualizar templates** con navegación específica

5. **Ejecutar configuración:**
```bash
python manage.py setup_roles --create-groups
```

## Usuarios Demo Incluidos

| Usuario | Password | Rol | Email |
|---------|----------|-----|-------|
| cliente_demo | demo123 | Cliente | cliente@demo.com |
| profesional_demo | demo123 | Profesional | profesional@demo.com |
| admin_demo | demo123 | Administrador | admin@demo.com |

## Testing

Para probar el sistema:

1. Crear usuarios demo: `python manage.py create_demo_users`
2. Iniciar servidor: `python manage.py runserver`
3. Probar login con diferentes roles
4. Verificar navegación y permisos específicos
5. Intentar acceder a URLs restringidas

El sistema está diseñado para ser robusto, seguro y fácil de mantener, siguiendo las mejores prácticas de Django y proporcionando una experiencia de usuario diferenciada según el rol.
