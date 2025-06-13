from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from .models import Perfil, Profesional
from .forms import (
    PerfilForm, UsuarioForm, ProfesionalForm, 
    HorariosProfesionalForm, EstadoProfesionalForm,
    ClienteRegistroForm
)
from .permissions import (
    RoleManager, 
    administrador_required, 
    profesional_required,
    role_required
)
from GestorSpa.apps.turnos.models import Turno
from GestorSpa.apps.servicios.models import Servicio
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.views.generic import CreateView

# Create your views here.

@login_required
def perfil(request):
    """Dashboard principal del usuario según su rol con edición unificada"""
    # Crear perfil si no existe
    if not hasattr(request.user, 'perfil'):
        Perfil.objects.create(usuario=request.user)

    user_role = RoleManager.get_user_role(request.user)
    
    # Contexto base
    context = {
        'user_role': user_role,
        'user_role_display': request.user.perfil.get_rol_display(),
    }
    
    # Manejar formularios POST
    if request.method == 'POST':
        # Formulario de datos profesionales
        if 'edit_profesional' in request.POST:
            if user_role == 'profesional':
                try:
                    profesional = request.user.profesional
                    profesional_form = ProfesionalForm(request.POST, request.FILES, instance=profesional)
                    if profesional_form.is_valid():
                        profesional_form.save()
                        messages.success(request, 'Datos profesionales actualizados correctamente.')
                        return redirect('usuarios:perfil')
                    else:
                        messages.error(request, 'Error al actualizar los datos profesionales. Revisa los campos.')
                except Profesional.DoesNotExist:
                    messages.error(request, 'No tienes un perfil profesional asignado.')
        
        # Formulario de perfil general
        elif 'edit_perfil' in request.POST:
            # Actualizar datos del usuario
            request.user.first_name = request.POST.get('first_name', '')
            request.user.last_name = request.POST.get('last_name', '')
            request.user.email = request.POST.get('email', '')
            request.user.save()
            
            # Actualizar datos del perfil
            perfil = request.user.perfil
            perfil.telefono = request.POST.get('telefono', '')
            perfil.direccion = request.POST.get('direccion', '')
            perfil.bio = request.POST.get('bio', '')
            
            # Manejar la foto de perfil
            if 'foto' in request.FILES:
                perfil.foto = request.FILES['foto']
            
            # Manejar la fecha de nacimiento
            fecha_nacimiento = request.POST.get('fecha_nacimiento')
            if fecha_nacimiento:
                perfil.fecha_nacimiento = fecha_nacimiento
            
            perfil.save()
            messages.success(request, 'Perfil general actualizado correctamente.')
            return redirect('usuarios:perfil')
    
    if user_role == 'cliente':
        # Dashboard para clientes - filtrar solo por usuario
        mis_turnos = Turno.objects.filter(
            usuario=request.user
        ).order_by('-fecha', '-hora_inicio')[:5]
        
        context.update({
            'mis_turnos': mis_turnos,
            'total_mis_turnos': mis_turnos.count(),
            'servicios_disponibles': Servicio.objects.filter(activo=True)[:6],
        })
        
    elif user_role == 'profesional':
        # Dashboard para profesionales con formularios de edición
        turnos_hoy = Turno.objects.filter(
            fecha__gte=timezone.now().date(),
            estado__in=['pendiente', 'confirmado']
        ).order_by('fecha', 'hora_inicio')[:10]
        
        # Preparar formulario de datos profesionales
        profesional_form = None
        profesional = None
        try:
            profesional = request.user.profesional
            profesional_form = ProfesionalForm(instance=profesional)
        except Profesional.DoesNotExist:
            messages.warning(request, 'No tienes un perfil profesional asignado.')
        
        # Preparar formulario de perfil general
        perfil_form_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'telefono': request.user.perfil.telefono,
            'direccion': request.user.perfil.direccion,
            'bio': request.user.perfil.bio,
            'fecha_nacimiento': request.user.perfil.fecha_nacimiento,
            'foto': request.user.perfil.foto,
        }
        
        context.update({
            'turnos_hoy': turnos_hoy,
            'turnos_pendientes': Turno.objects.filter(estado='pendiente').count(),
            'servicios_count': Servicio.objects.filter(activo=True).count(),
            'profesional': profesional,
            'profesional_form': profesional_form,
            'perfil_form_data': perfil_form_data,
        })
        
    elif user_role == 'administrador':
        # Dashboard para administradores
        from django.db.models import Count
        
        total_usuarios = User.objects.count()
        total_profesionales = Profesional.objects.count()
        turnos_count = Turno.objects.count()
        servicios_count = Servicio.objects.count()
        turnos_hoy = Turno.objects.filter(fecha=timezone.now().date()).count()
        # Obtener los últimos 5 turnos
        ultimos_turnos = Turno.objects.all().order_by('-fecha', '-hora_inicio')[:5]
        # Estadísticas por estado
        turnos_por_estado = Turno.objects.values('estado').annotate(
            total=Count('id')
        )
        
        context.update({
            'total_usuarios': total_usuarios,
            'total_profesionales': total_profesionales,
            'turnos_count': turnos_count,
            'servicios_count': servicios_count,
            'turnos_hoy': turnos_hoy,
            'ultimos_turnos': ultimos_turnos,
            'turnos_por_estado': turnos_por_estado,
        })
    
    return render(request, 'usuarios/perfil.html', context)


@administrador_required
def gestionar_usuarios(request):
    """Vista para gestionar usuarios - Solo administradores"""
    usuarios = User.objects.all().select_related('perfil')
    
    context = {
        'usuarios': usuarios,
        'roles_disponibles': RoleManager.get_available_roles(),
    }
    
    return render(request, 'usuarios/gestionar_usuarios.html', context)


@administrador_required  
def asignar_rol_usuario(request, user_id):
    """Vista para asignar rol a usuario - Solo administradores"""
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            nuevo_rol = request.POST.get('rol')
            
            if nuevo_rol in dict(RoleManager.get_available_roles()):
                RoleManager.assign_role_to_user(user, nuevo_rol)
                messages.success(
                    request, 
                    f'Rol "{RoleManager.ROLES[nuevo_rol]["name"]}" asignado a {user.username}'
                )
            else:
                messages.error(request, 'Rol inválido')
                
        except User.DoesNotExist:
            messages.error(request, 'Usuario no encontrado')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    
    return redirect('usuarios:gestionar_usuarios')


@role_required('cliente', 'administrador')
def mis_turnos(request):
    """Vista para que los clientes vean sus propios turnos"""
    user_role = RoleManager.get_user_role(request.user)
    
    if user_role == 'cliente':
        # Filtrar turnos del cliente solo por usuario
        turnos = Turno.objects.filter(
            usuario=request.user
        ).order_by('-fecha', '-hora_inicio')
    else:
        # Los administradores ven todos
        turnos = Turno.objects.all().order_by('-fecha', '-hora_inicio')
    
    context = {
        'turnos': turnos,
        'is_cliente': user_role == 'cliente'
    }
    
    return render(request, 'usuarios/mis_turnos.html', context)


@login_required
@profesional_required
def perfil_profesional(request):
    """Vista para que los profesionales gestionen su información"""
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        # Crear perfil profesional si no existe
        profesional = Profesional.objects.create(
            usuario=request.user,
            nombre_completo=f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            contacto=request.user.email,
            especialidad="Sin especificar",
            numero_matricula=f"TEMP-{request.user.id}",
            fecha_inicio=timezone.now().date()
        )
        messages.info(request, 'Se ha creado tu perfil profesional. Por favor, completa tu información.')
    
    # Estadísticas para el profesional
    mis_turnos = Turno.objects.filter(
        estado__in=['pendiente', 'confirmado']
    ).order_by('fecha', 'hora_inicio')[:10]
    
    turnos_hoy = Turno.objects.filter(
        fecha=timezone.now().date(),
        estado__in=['pendiente', 'confirmado']
    ).count()
    
    context = {
        'profesional': profesional,
        'mis_turnos': mis_turnos,
        'turnos_hoy': turnos_hoy,
        'servicios_count': Servicio.objects.filter(activo=True).count(),        'horarios_semana': profesional.get_horarios_semana(),
    }
    
    return render(request, 'usuarios/perfil_profesional.html', context)


@login_required
@profesional_required
def editar_horarios_profesional(request):
    """Vista para editar horarios de disponibilidad"""
    try:
        profesional = request.user.profesional
    except Profesional.DoesNotExist:
        messages.error(request, 'No tienes un perfil profesional asignado.')
        return redirect('usuarios:perfil')
    
    if request.method == 'POST':
        form = HorariosProfesionalForm(request.POST, instance=profesional)
        if form.is_valid():
            form.save()
            messages.success(request, 'Horarios de disponibilidad actualizados correctamente.')
            return redirect('usuarios:perfil_profesional')
    else:
        form = HorariosProfesionalForm(instance=profesional)
    
    context = {
        'form': form,
        'profesional': profesional,
        'dias_semana': ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'],
    }
    
    return render(request, 'usuarios/editar_horarios_profesional.html', context)


@login_required
@administrador_required
def gestionar_profesionales(request):
    """Vista para administradores para gestionar profesionales"""
    profesionales = Profesional.objects.all().order_by('nombre_completo')
    
    context = {
        'profesionales': profesionales,
        'total_profesionales': profesionales.count(),
        'profesionales_activos': profesionales.filter(estado='activo').count(),
    }
    
    return render(request, 'usuarios/gestionar_profesionales.html', context)


@login_required
@administrador_required
def detalle_profesional(request, profesional_id):
    """Vista detallada de un profesional para administradores"""
    profesional = get_object_or_404(Profesional, id=profesional_id)
    
    # Turnos del profesional (esto se conectará cuando se implemente la asignación)
    turnos_profesional = Turno.objects.filter(
        # fecha__gte=timezone.now().date()  # Filtrar futuros cuando se conecte
    ).order_by('fecha', 'hora_inicio')[:10]
    
    context = {
        'profesional': profesional,
        'turnos_profesional': turnos_profesional,
        'horarios_semana': profesional.get_horarios_semana(),
        'especialidades': profesional.get_especialidades_todas(),
    }
    
    return render(request, 'usuarios/detalle_profesional.html', context)


@login_required
@administrador_required
def cambiar_estado_profesional(request, profesional_id):
    """Vista para cambiar el estado de un profesional"""
    profesional = get_object_or_404(Profesional, id=profesional_id)
    
    if request.method == 'POST':
        form = EstadoProfesionalForm(request.POST, instance=profesional)
        if form.is_valid():
            form.save()
            messages.success(request, f'Estado de {profesional.nombre_completo} actualizado correctamente.')
            return redirect('usuarios:detalle_profesional', profesional_id=profesional.id)
    else:
        form = EstadoProfesionalForm(instance=profesional)
    
    context = {
        'form': form,
        'profesional': profesional,
    }
    
    return render(request, 'usuarios/cambiar_estado_profesional.html', context)


@login_required
def api_horarios_profesional(request, profesional_id):
    """API para obtener horarios de un profesional (para uso en turnos)"""
    try:
        profesional = get_object_or_404(Profesional, id=profesional_id, estado='activo')
        horarios = profesional.get_horarios_semana()
        
        return JsonResponse({
            'success': True,
            'horarios': horarios,
            'profesional': {
                'id': profesional.id,
                'nombre': profesional.get_nombre_display(),
                'especialidad': profesional.especialidad
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


class ClienteRegistroView(CreateView):
    """Vista para registro de nuevos clientes"""
    
    form_class = ClienteRegistroForm
    template_name = 'usuarios/registro_cliente.html'
    success_url = reverse_lazy('turnos:turno_reserva_unificada')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Loguear automáticamente al usuario después del registro
        login(self.request, self.object)
        messages.success(
            self.request, 
            f'¡Bienvenido/a {self.object.first_name}! Tu cuenta ha sido creada exitosamente. Ahora puedes hacer tu reserva.'
        )
        return response
    
    def form_invalid(self, form):
        messages.error(
            self.request,
            'Por favor, corrige los errores en el formulario.'
        )
        return super().form_invalid(form)


@login_required
def test_perfil(request):
    """Vista de prueba para el dashboard de administrador"""
    from GestorSpa.apps.usuarios.permissions import RoleManager
    from django.db.models import Count
    from GestorSpa.apps.turnos.models import Turno
    from GestorSpa.apps.servicios.models import Servicio
    from GestorSpa.apps.usuarios.models import Profesional

    user_role = RoleManager.get_user_role(request.user)
    
    context = {
        'user_role': user_role,
        'user_role_display': request.user.perfil.get_rol_display(),
        'total_usuarios': User.objects.count(),
        'total_profesionales': Profesional.objects.count(),
        'turnos_count': Turno.objects.count(),
        'servicios_count': Servicio.objects.count(),
    }
    
    return render(request, 'usuarios/test_perfil.html', context)
