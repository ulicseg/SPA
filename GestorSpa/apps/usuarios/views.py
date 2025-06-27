from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from datetime import date, timedelta
from .models import Perfil, Profesional
from .forms import (
    PerfilForm, UsuarioForm, ProfesionalForm, 
    HorariosProfesionalForm, EstadoProfesionalForm,
    ClienteRegistroForm, UserForm
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

@login_required
def perfil(request):
    user = request.user
    role_manager = RoleManager() # Instanciar RoleManager
    user_role = role_manager.get_user_role(user)

    if user_role == 'administrador':
        try:
            total_usuarios = User.objects.count()
            total_profesionales = Profesional.objects.count()
            turnos_count = Turno.objects.count()
            servicios_count = Servicio.objects.count()
            turnos_hoy = Turno.objects.filter(fecha=timezone.now().date()).count()
            ultimos_turnos = Turno.objects.all().order_by('-fecha', '-hora_inicio')[:5]
            turnos_por_estado = Turno.objects.values('estado').annotate(total=Count('id'))
            
            context = {
                'total_usuarios': total_usuarios,
                'total_profesionales': total_profesionales,
                'turnos_count': turnos_count,
                'servicios_count': servicios_count,
                'turnos_hoy': turnos_hoy,
                'ultimos_turnos': ultimos_turnos,
                'turnos_por_estado': turnos_por_estado,
                'user_role_display': 'Administrador',
                'user_role': 'administrador',
                'today': date.today(),
                'tomorrow': date.today() + timedelta(days=1),
            }
            return render(request, 'usuarios/perfil.html', context)
        except Exception as e:
            messages.error(request, f"Error al cargar el perfil de administrador: {e}")
            # Considera redirigir a una página de error o mostrar un mensaje más amigable
            return render(request, 'usuarios/perfil.html', {'user_role_display': 'Administrador', 'user_role': 'administrador'})

    elif user_role == 'profesional':
        try:
            profesional = user.profesional # Access Profesional instance from User
            
            # Manejar formularios de edición de perfil
            if request.method == 'POST':
                if 'edit_perfil' in request.POST:
                    # Editar información personal del usuario
                    usuario_form = UsuarioForm(request.POST, instance=user)
                    perfil_form = PerfilForm(request.POST, request.FILES, instance=user.perfil if hasattr(user, 'perfil') else None)
                    
                    if usuario_form.is_valid() and perfil_form.is_valid():
                        # Guardar datos del usuario
                        usuario_form.save()
                        
                        # Guardar perfil
                        perfil = perfil_form.save(commit=False)
                        perfil.usuario = user
                        perfil.save()
                        
                        # Sincronizar datos con el modelo Profesional
                        if hasattr(user, 'profesional'):
                            profesional = user.profesional
                            # Actualizar nombre completo en el profesional
                            profesional.nombre_completo = f"{user.first_name} {user.last_name}".strip()
                            # Sincronizar teléfono si se actualizó
                            if perfil.telefono and not profesional.telefono_profesional:
                                profesional.telefono_profesional = perfil.telefono
                            profesional.save()
                        
                        messages.success(request, 'Perfil personal actualizado correctamente.')
                        return redirect('usuarios:perfil')
                    else:
                        messages.error(request, 'Error al actualizar el perfil personal. Verifica los datos.')
                        
                elif 'edit_profesional' in request.POST:
                    # Editar información profesional
                    profesional_form = ProfesionalForm(request.POST, request.FILES, instance=profesional)
                    
                    if profesional_form.is_valid():
                        profesional_form.save()
                        messages.success(request, 'Información profesional actualizada correctamente.')
                        return redirect('usuarios:perfil')
                    else:
                        messages.error(request, 'Error al actualizar la información profesional. Verifica los datos.')            # Obtener datos de turnos (excluyendo cancelados del dashboard)
            turnos_asignados = Turno.objects.filter(profesional=profesional).order_by('-fecha', '-hora_inicio')
            turnos_activos = turnos_asignados.exclude(estado='cancelado')  # Filtrar cancelados para el dashboard
            turnos_pendientes = turnos_activos.filter(estado='pendiente').count()
            turnos_completados = turnos_activos.filter(estado='completado').count()
            turnos_hoy = turnos_activos.filter(fecha=timezone.now().date()).order_by('hora_inicio')
            turnos_hoy_profesional = turnos_hoy.count()
            # Próximos turnos (futuros, no incluye hoy)
            ultimos_turnos = turnos_activos.filter(fecha__gt=timezone.now().date()).order_by('fecha', 'hora_inicio')[:5]
              # Preparar formularios para el template
            profesional_form = ProfesionalForm(instance=profesional)
            
            # Inicializar nombre_completo si está vacío
            if not profesional.nombre_completo:
                nombre_completo = f"{user.first_name} {user.last_name}".strip()
                if nombre_completo:
                    profesional.nombre_completo = nombre_completo
                    profesional.save()
            
            # Obtener datos del perfil personal
            perfil_data = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            }
              # Agregar datos del perfil si existe
            if hasattr(user, 'perfil'):
                perfil_data.update({
                    'telefono': user.perfil.telefono,
                    'fecha_nacimiento': user.perfil.fecha_nacimiento,
                    'foto': user.perfil.foto,
                    'bio': user.perfil.bio,                    'direccion': getattr(user.perfil, 'direccion', ''),
                })
            
            context = {
                'profesional': profesional,
                'turnos_asignados': turnos_activos[:10], # Limitar para la vista (sin cancelados)
                'total_turnos_asignados': turnos_activos.count(),  # Solo turnos activos
                'turnos_pendientes': turnos_pendientes,
                'turnos_completados': turnos_completados,
                'turnos_hoy': turnos_hoy,  # Lista de turnos de hoy (sin cancelados)
                'turnos_hoy_profesional': turnos_hoy_profesional,  # Contador
                'ultimos_turnos': ultimos_turnos,  # Próximos turnos (sin cancelados)
                'user_role_display': 'Profesional',
                'user_role': 'profesional',
                'horarios_semana': profesional.get_horarios_semana() if hasattr(profesional, 'get_horarios_semana') else [],
                'especialidades': profesional.get_especialidades_todas() if hasattr(profesional, 'get_especialidades_todas') else [],
                # Formularios para edición
                'profesional_form': profesional_form,
                'perfil_form_data': perfil_data,            }
            # Usar el template perfil_profesional.html para profesionales
            return render(request, 'usuarios/perfil_profesional.html', context)
        except Profesional.DoesNotExist:
            messages.error(request, "No se encontró tu perfil profesional. Por favor, contacta al administrador.")
            return redirect('home') 
        except Exception as e:
            messages.error(request, f"Error al cargar el perfil profesional: {e}")
            return redirect('home')
    elif user_role == 'cliente':
        try:
            # Manejar formularios de edición de perfil para clientes
            if request.method == 'POST':
                if 'edit_perfil' in request.POST:
                    # Editar información personal del usuario
                    usuario_form = UsuarioForm(request.POST, instance=user)
                    perfil_form = PerfilForm(request.POST, request.FILES, instance=user.perfil if hasattr(user, 'perfil') else None)
                    
                    if usuario_form.is_valid() and perfil_form.is_valid():
                        usuario_form.save()
                        perfil = perfil_form.save(commit=False)
                        perfil.usuario = user
                        perfil.save()
                        messages.success(request, 'Perfil actualizado correctamente.')
                        return redirect('usuarios:perfil')
                    else:
                        messages.error(request, 'Error al actualizar el perfil. Verifica los datos.')
            
            # Obtener turnos del cliente
            turnos_cliente = Turno.objects.filter(usuario=user).order_by('-fecha', '-hora_inicio')
            mis_turnos = turnos_cliente[:5]  # Últimos 5 turnos
            servicios_disponibles = Servicio.objects.filter(activo=True)[:5]  # Primeros 5 servicios activos
            
            # Preparar datos del perfil personal
            perfil_data = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
            }
            
            # Agregar datos del perfil si existe
            if hasattr(user, 'perfil'):
                perfil_data.update({
                    'telefono': user.perfil.telefono,
                    'fecha_nacimiento': user.perfil.fecha_nacimiento,
                    'foto': user.perfil.foto,
                    'bio': user.perfil.bio,
                    'direccion': getattr(user.perfil, 'direccion', ''),
                })
            
            context = {
                'user_role_display': 'Cliente',
                'user_role': 'cliente',
                'mis_turnos': mis_turnos,
                'total_turnos_cliente': turnos_cliente.count(),
                'servicios_disponibles': servicios_disponibles,
                # Formularios para edición
                'perfil_form_data': perfil_data,
            }
            return render(request, 'usuarios/perfil.html', context)
        except Exception as e:
            messages.error(request, f"Error al cargar el perfil de cliente: {e}")
            return redirect('home')
            
    else:
        # Rol desconocido o sin perfil asignado
        messages.warning(request, "No tienes un rol asignado o tu perfil no está completo.")
        return redirect('home')

@administrador_required
def gestionar_usuarios(request):
    """Vista para gestionar usuarios - Solo administradores"""
    usuarios = User.objects.all().select_related('perfil')
    
    context = {
        'usuarios': usuarios,
        'roles_disponibles': RoleManager.get_available_roles(),
    }
    
    return render(request, 'usuarios/gestionar_usuarios.html', context)

@login_required
@administrador_required
def eliminar_usuario(request, user_id):
    """Vista para eliminar un usuario - Solo administradores"""
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, id=user_id)
            
            # Verificar que no se puede eliminar el superusuario o el administrador actual
            if user.is_superuser:
                messages.error(request, 'No se puede eliminar un superusuario.')
                return redirect('usuarios:gestionar_usuarios')
            
            if user == request.user:
                messages.error(request, 'No puedes eliminar tu propia cuenta.')
                return redirect('usuarios:gestionar_usuarios')
            
            # Guardar información para el mensaje
            username = user.username
            user_name = f"{user.first_name} {user.last_name}".strip() or user.username
            
            # Eliminar el usuario (esto también eliminará automáticamente los perfiles relacionados)
            user.delete()
            
            messages.success(request, f'Usuario "{user_name}" ({username}) eliminado exitosamente.')
            
        except Exception as e:
            messages.error(request, f'Error al eliminar el usuario: {str(e)}')
    else:
        messages.error(request, 'Método no permitido.')
    
    return redirect('usuarios:gestionar_usuarios')


@role_required('cliente', 'profesional', 'administrador')
def mis_turnos(request):
    """Vista para que los usuarios vean sus turnos (clientes: sus reservas, profesionales: sus asignaciones)"""
    user_role = RoleManager.get_user_role(request.user)
    
    if user_role == 'cliente':
        # Filtrar turnos del cliente solo por usuario
        turnos = Turno.objects.filter(
            usuario=request.user
        ).order_by('-fecha', '-hora_inicio')
    elif user_role == 'profesional':
        # Filtrar turnos asignados al profesional
        try:
            profesional = request.user.profesional
            turnos = Turno.objects.filter(
                profesional=profesional
            ).order_by('-fecha', '-hora_inicio')
        except Profesional.DoesNotExist:
            turnos = Turno.objects.none()
    else:
        # Los administradores ven todos
        turnos = Turno.objects.all().order_by('-fecha', '-hora_inicio')
    
    # Calcular estadísticas de turnos
    total_turnos = turnos.count()
    pendientes = turnos.filter(estado='pendiente').count()
    confirmados = turnos.filter(estado='confirmado').count()
    completados = turnos.filter(estado='completado').count()
    cancelados = turnos.filter(estado='cancelado').count()
    
    context = {
        'turnos': turnos,
        'is_cliente': user_role == 'cliente',
        'is_profesional': user_role == 'profesional',
        'user_role': user_role,
        'total_turnos': total_turnos,
        'pendientes': pendientes,
        'confirmados': confirmados,
        'completados': completados,
        'cancelados': cancelados,
    }
    
    return render(request, 'usuarios/mis_turnos.html', context)


@login_required
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
            return redirect('usuarios:perfil')
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
@administrador_required
def crear_profesional(request):
    """Vista para crear un nuevo profesional"""
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profesional_form = ProfesionalForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profesional_form.is_valid():
            try:
                # Crear el usuario con el formulario (esto asignará automáticamente el grupo)
                user = user_form.save(commit=True)
                user.is_staff = True  # Los profesionales pueden acceder al admin
                user.save()
                
                # Asignar el rol de profesional
                perfil, created = Perfil.objects.get_or_create(usuario=user)
                perfil.rol = 'profesional'
                perfil.tipo_usuario = 'profesional'  # Asegurar que el tipo también se asigne
                perfil.save()
                
                # Crear el profesional
                profesional = profesional_form.save(commit=False)
                profesional.usuario = user
                # Establecer fecha de inicio automáticamente
                from django.utils import timezone
                profesional.fecha_inicio = timezone.now().date()
                profesional.save()
                profesional_form.save_m2m()  # Para los servicios_especialidad
                
                messages.success(request, f'Profesional {profesional.nombre_completo} creado exitosamente.')
                return redirect('usuarios:detalle_profesional', profesional_id=profesional.id)
                
            except Exception as e:
                messages.error(request, f'Error al crear el profesional: {str(e)}')
                # Si hay error, eliminar el usuario si se creó
                if 'user' in locals():
                    user.delete()
    else:
        user_form = UserForm()
        profesional_form = ProfesionalForm()
    
    context = {
        'user_form': user_form,
        'profesional_form': profesional_form,
        'is_create': True,
    }
    
    return render(request, 'usuarios/crear_profesional.html', context)


@login_required
@profesional_required
def marcar_turno_completado(request, turno_id):
    """
    Vista para que el profesional marque un turno como completado
    """
    from GestorSpa.apps.turnos.models import Turno
    
    if request.method == 'POST':
        try:
            # Obtener el turno y verificar que pertenece al profesional logueado
            turno = get_object_or_404(Turno, id=turno_id, profesional=request.user.profesional)
            
            # Usar el nuevo método de cambio de estado
            if turno.puede_ser_completado():
                turno.cambiar_estado('completado', request.user)
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Turno marcado como completado exitosamente.'
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'message': f'El turno no puede ser completado. Estado actual: {turno.get_estado_display()}'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Error al actualizar el turno: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


@login_required
@administrador_required
def cambiar_estado_turno(request, turno_id):
    """
    Vista para que los administradores cambien el estado de turnos
    """
    from GestorSpa.apps.turnos.models import Turno
    
    if request.method == 'POST':
        try:
            turno = get_object_or_404(Turno, id=turno_id)
            nuevo_estado = request.POST.get('estado')
            
            # Validar que el nuevo estado es válido
            estados_validos = dict(Turno.ESTADO_CHOICES)
            if nuevo_estado not in estados_validos:
                messages.error(request, 'Estado inválido.')
                return redirect('turnos:turno_detail', pk=turno_id)
            
            # Usar el método de cambio de estado del modelo
            try:
                turno.cambiar_estado(nuevo_estado, request.user)
                messages.success(
                    request, 
                    f'Estado del turno cambiado a: {estados_validos[nuevo_estado]}'
                )
            except Exception as e:
                messages.error(request, str(e))
                
        except Exception as e:
            messages.error(request, f'Error al cambiar estado: {str(e)}')
    
    return redirect('turnos:turno_detail', pk=turno_id)

@login_required
@administrador_required
def ejecutar_autocompletado_turnos(request):
    """Vista para ejecutar manualmente el auto-completado de turnos"""
    try:
        resultado = Turno.marcar_completados_automaticamente()
        
        if resultado['turnos_marcados'] > 0:
            messages.success(
                request, 
                f"✓ Se marcaron {resultado['turnos_marcados']} turnos como completados automáticamente."
            )
        else:
            messages.info(
                request, 
                "No se encontraron turnos que necesiten ser marcados como completados."
            )
        
        # Mostrar errores si los hay
        for error in resultado['errores']:
            messages.error(request, f"Error: {error}")
            
    except Exception as e:
        messages.error(request, f"Error al ejecutar auto-completado: {str(e)}")
    
    return redirect('usuarios:perfil')

