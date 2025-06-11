from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.generic import ListView, UpdateView, DetailView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db import models
from .models import Perfil, Profesional, EspecialidadSecundaria
from .forms import PerfilForm, ProfesionalForm, UserProfesionalForm
from .permissions import AdministradorRequiredMixin, ClienteRequiredMixin, PersonalAutorizadoRequiredMixin, ProfesionalRequiredMixin
from GestorSpa.apps.turnos.models import Turno
from GestorSpa.apps.servicios.models import Servicio

# Create your views here.

@login_required
def perfil(request):
    # Crear perfil si no existe
    if not hasattr(request.user, 'perfil'):
        Perfil.objects.create(usuario=request.user)
    
    # Obtener estadísticas según el rol
    perfil_usuario = request.user.perfil
    
    if perfil_usuario.rol == 'cliente':
        # Los clientes solo ven sus propios turnos
        turnos_count = Turno.objects.filter(email=request.user.email).count()
        ultimos_turnos = Turno.objects.filter(email=request.user.email).order_by('-fecha', '-hora_inicio')[:5]
        servicios_count = Servicio.objects.filter(activo=True).count()
    else:
        # Profesionales y administradores ven todas las estadísticas
        turnos_count = Turno.objects.count()
        servicios_count = Servicio.objects.count()
        ultimos_turnos = Turno.objects.all().order_by('-fecha', '-hora_inicio')[:5]

    context = {
        'turnos_count': turnos_count,
        'servicios_count': servicios_count,
        'ultimos_turnos': ultimos_turnos,
        'rol_usuario': perfil_usuario.get_rol_display(),
    }
    return render(request, 'perfil.html', context)

@login_required
def perfil_edit(request):
    # Asegurarse de que existe el perfil
    if not hasattr(request.user, 'perfil'):
        Perfil.objects.create(usuario=request.user)
    
    if request.method == 'POST':
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
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('usuarios:perfil')
    
    return render(request, 'perfil_edit.html', {'user': request.user})

class UsuarioListView(AdministradorRequiredMixin, ListView):
    """Vista para listar todos los usuarios (solo administradores)"""
    model = User
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'
    paginate_by = 20
    
    def get_queryset(self):
        return User.objects.select_related('perfil').order_by('username')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_usuarios'] = User.objects.count()
        context['clientes_count'] = Perfil.objects.filter(rol='cliente').count()
        context['profesionales_count'] = Perfil.objects.filter(rol='profesional').count()
        context['administradores_count'] = Perfil.objects.filter(rol='administrador').count()
        return context


class PerfilUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para que los usuarios editen su propio perfil"""
    model = Perfil
    fields = ['telefono', 'direccion', 'foto', 'bio', 'fecha_nacimiento']
    template_name = 'usuarios/perfil_edit.html'
    success_url = reverse_lazy('usuarios:perfil')
    
    def get_object(self, queryset=None):
        # Solo permite editar el propio perfil
        if not hasattr(self.request.user, 'perfil'):
            Perfil.objects.create(usuario=self.request.user)
        return self.request.user.perfil
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil actualizado exitosamente.')
        return super().form_valid(form)


class AsignarRolView(AdministradorRequiredMixin, UpdateView):
    """Vista para que los administradores asignen roles a usuarios"""
    model = Perfil
    fields = ['rol']
    template_name = 'usuarios/asignar_rol.html'
    success_url = reverse_lazy('usuarios:usuario_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['usuario_objetivo'] = self.object.usuario
        return context
    
    def form_valid(self, form):
        usuario_objetivo = form.instance.usuario
        nuevo_rol = form.cleaned_data['rol']
        messages.success(
            self.request, 
            f'Rol de {usuario_objetivo.username} cambiado a {form.instance.get_rol_display()}'
        )
        return super().form_valid(form)


@login_required
def dashboard_rol(request):
    """Vista de dashboard específica según el rol del usuario"""
    if not hasattr(request.user, 'perfil'):
        Perfil.objects.create(usuario=request.user)
    
    perfil = request.user.perfil
    context = {'perfil': perfil}
    
    if perfil.rol == 'cliente':
        # Dashboard para clientes
        mis_turnos = Turno.objects.filter(email=request.user.email).order_by('-fecha')[:5]
        servicios_disponibles = Servicio.objects.filter(activo=True)[:6]
        context.update({
            'mis_turnos': mis_turnos,
            'servicios_disponibles': servicios_disponibles,
            'total_mis_turnos': Turno.objects.filter(email=request.user.email).count()
        })
        return render(request, 'usuarios/dashboard_cliente.html', context)
    
    elif perfil.rol == 'profesional':
        # Dashboard para profesionales
        turnos_hoy = Turno.objects.filter(fecha=timezone.now().date()).order_by('hora_inicio')
        turnos_pendientes = Turno.objects.filter(estado='pendiente').count()
        context.update({
            'turnos_hoy': turnos_hoy,
            'turnos_pendientes': turnos_pendientes,
            'total_turnos': Turno.objects.count()
        })
        return render(request, 'usuarios/dashboard_profesional.html', context)
    
    elif perfil.rol == 'administrador':
        # Dashboard para administradores
        hoy = timezone.now().date()
        hace_una_semana = hoy - timedelta(days=7)
        
        stats = {
            'total_turnos': Turno.objects.count(),
            'turnos_hoy': Turno.objects.filter(fecha=hoy).count(),
            'turnos_semana': Turno.objects.filter(fecha__gte=hace_una_semana).count(),
            'total_servicios': Servicio.objects.count(),
            'total_usuarios': User.objects.count(),
            'turnos_pendientes': Turno.objects.filter(estado='pendiente').count(),
        }
        
        ultimos_turnos = Turno.objects.order_by('-created_at')[:10]
        
        context.update({
            'stats': stats,
            'ultimos_turnos': ultimos_turnos
        })
        return render(request, 'usuarios/dashboard_administrador.html', context)
    
    else:
        return render(request, 'usuarios/dashboard_default.html', context)

@login_required
def perfil_profesional(request):
    """Vista para que los profesionales vean y editen su perfil específico"""
    # Verificar que el usuario tiene rol de profesional
    if not hasattr(request.user, 'perfil') or request.user.perfil.rol != 'profesional':
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('usuarios:perfil')
    
    # Crear el modelo Profesional si no existe
    profesional, created = Profesional.objects.get_or_create(
        usuario=request.user,
        defaults={
            'nombre_completo': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'telefono': request.user.perfil.telefono or '',
            'especialidad': 'spa',
        }
    )
    
    if created:
        messages.info(request, 'Se ha creado tu perfil profesional. Por favor, completa tu información.')
    
    context = {
        'profesional': profesional,
        'turnos_hoy': Turno.objects.filter(
            fecha=timezone.now().date(),
            estado__in=['confirmado', 'en_progreso']
        ).count(),
        'turnos_semana': Turno.objects.filter(
            fecha__gte=timezone.now().date(),
            fecha__lte=timezone.now().date() + timedelta(days=7)
        ).count(),
        'servicios_ofrecidos': profesional.servicios_que_ofrece.filter(activo=True).count(),
    }
    
    return render(request, 'usuarios/profesional_perfil.html', context)


class ProfesionalUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Vista para que los profesionales actualicen su información"""
    model = Profesional
    form_class = ProfesionalForm
    template_name = 'usuarios/profesional_editar.html'
    success_url = reverse_lazy('usuarios:perfil_profesional')
    
    def test_func(self):
        """Solo permitir a profesionales editar su propio perfil"""
        return (hasattr(self.request.user, 'perfil') and 
                self.request.user.perfil.rol == 'profesional')
    
    def get_object(self):
        """Obtener o crear el objeto Profesional para el usuario actual"""
        profesional, created = Profesional.objects.get_or_create(
            usuario=self.request.user,
            defaults={
                'nombre_completo': f"{self.request.user.first_name} {self.request.user.last_name}".strip() or self.request.user.username,
                'telefono': getattr(self.request.user.perfil, 'telefono', '') or '',
                'especialidad': 'spa',
            }
        )
        return profesional
    
    def get_form_kwargs(self):
        """Pasar el usuario al formulario"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Procesar el formulario válido"""
        messages.success(self.request, 'Tu información profesional ha sido actualizada exitosamente.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Manejar formulario inválido"""
        messages.error(self.request, 'Por favor, corrige los errores en el formulario.')
        return super().form_invalid(form)


class ProfesionalListView(LoginRequiredMixin, ListView):
    """Vista para listar todos los profesionales activos"""
    model = Profesional
    template_name = 'usuarios/profesional_lista.html'
    context_object_name = 'profesionales'
    paginate_by = 12
    
    def get_queryset(self):
        """Filtrar solo profesionales activos"""
        queryset = Profesional.objects.filter(activo=True).select_related('usuario')
        
        # Filtrar por especialidad si se proporciona
        especialidad = self.request.GET.get('especialidad')
        if especialidad:
            queryset = queryset.filter(especialidad=especialidad)
        
        # Búsqueda por nombre
        busqueda = self.request.GET.get('buscar')
        if busqueda:
            queryset = queryset.filter(nombre_completo__icontains=busqueda)
        
        return queryset.order_by('nombre_completo')
    
    def get_context_data(self, **kwargs):
        """Añadir contexto adicional"""
        context = super().get_context_data(**kwargs)
        context['especialidades'] = Profesional.ESPECIALIDADES_CHOICES
        context['especialidad_actual'] = self.request.GET.get('especialidad', '')
        context['busqueda_actual'] = self.request.GET.get('buscar', '')
        return context


class ProfesionalDetailView(LoginRequiredMixin, DetailView):
    """Vista detalle de un profesional"""
    model = Profesional
    template_name = 'usuarios/profesional_detalle.html'
    context_object_name = 'profesional'
    
    def get_queryset(self):
        """Solo mostrar profesionales activos"""
        return Profesional.objects.filter(activo=True).select_related('usuario')
    
    def get_context_data(self, **kwargs):
        """Añadir servicios y horarios al contexto"""
        context = super().get_context_data(**kwargs)
        context['servicios'] = self.object.servicios_que_ofrece.filter(activo=True)
        context['dias_disponibles'] = self.object.get_dias_disponibles_list()
        return context


@login_required
def ajax_profesionales_por_servicio(request):
    """Vista AJAX para obtener profesionales que ofrecen un servicio específico"""
    servicio_id = request.GET.get('servicio_id')
    
    if not servicio_id:
        return JsonResponse({'error': 'ID de servicio requerido'}, status=400)
    
    try:
        profesionales = Profesional.objects.filter(
            servicios_que_ofrece__id=servicio_id,
            activo=True
        ).values('id', 'nombre_completo', 'especialidad')
        
        return JsonResponse({
            'profesionales': list(profesionales)
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class ProfesionalGestionView(AdministradorRequiredMixin, ListView):
    """Vista para gestión completa de profesionales por administradores"""
    model = Profesional
    template_name = 'usuarios/profesional_gestion.html'
    context_object_name = 'profesionales'
    paginate_by = 15
    
    def get_queryset(self):
        """Filtrar profesionales con opciones de búsqueda"""
        queryset = Profesional.objects.select_related('usuario').prefetch_related('servicios_que_ofrece')
        
        # Filtros disponibles
        especialidad = self.request.GET.get('especialidad')
        if especialidad:
            queryset = queryset.filter(especialidad=especialidad)
        
        estado = self.request.GET.get('estado')
        if estado == 'activo':
            queryset = queryset.filter(activo=True)
        elif estado == 'inactivo':
            queryset = queryset.filter(activo=False)
        
        busqueda = self.request.GET.get('buscar')
        if busqueda:
            queryset = queryset.filter(
                models.Q(nombre_completo__icontains=busqueda) |
                models.Q(usuario__username__icontains=busqueda) |
                models.Q(usuario__email__icontains=busqueda) |
                models.Q(telefono__icontains=busqueda)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Añadir estadísticas y datos de contexto"""
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        context['total_profesionales'] = Profesional.objects.count()
        context['profesionales_activos'] = Profesional.objects.filter(activo=True).count()
        context['profesionales_inactivos'] = Profesional.objects.filter(activo=False).count()
        
        # Estadísticas por especialidad
        especialidades_stats = {}
        for codigo, nombre in Profesional.ESPECIALIDADES_CHOICES:
            count = Profesional.objects.filter(especialidad=codigo, activo=True).count()
            if count > 0:
                especialidades_stats[nombre] = count
        context['especialidades_stats'] = especialidades_stats
        
        # Opciones de filtrado
        context['especialidades'] = Profesional.ESPECIALIDADES_CHOICES
        context['especialidad_actual'] = self.request.GET.get('especialidad', '')
        context['estado_actual'] = self.request.GET.get('estado', '')
        context['busqueda_actual'] = self.request.GET.get('buscar', '')
        
        # Servicios disponibles para asignación
        context['servicios_disponibles'] = Servicio.objects.filter(activo=True)
        
        return context


class ProfesionalCreateView(AdministradorRequiredMixin, CreateView):
    """Vista para crear nuevos profesionales por administradores"""
    model = Profesional
    template_name = 'usuarios/profesional_crear.html'
    fields = [
        'usuario', 'nombre_completo', 'especialidad', 'telefono', 
        'email_profesional', 'numero_licencia', 'años_experiencia',
        'certificaciones', 'hora_inicio_disponibilidad', 
        'hora_fin_disponibilidad', 'dias_disponibles', 'biografia',
        'foto_profesional', 'servicios_que_ofrece', 'fecha_contratacion', 'activo'
    ]
    success_url = reverse_lazy('usuarios:profesional_gestion')
    
    def form_valid(self, form):
        """Validar y crear profesional"""
        # Asegurar que el usuario tenga rol de profesional
        usuario = form.cleaned_data['usuario']
        if hasattr(usuario, 'perfil'):
            if usuario.perfil.rol != 'profesional':
                usuario.perfil.rol = 'profesional'
                usuario.perfil.save()
        else:
            Perfil.objects.create(usuario=usuario, rol='profesional')
        
        messages.success(
            self.request, 
            f'Profesional {form.cleaned_data["nombre_completo"]} creado exitosamente.'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Solo usuarios sin perfil profesional o con rol profesional
        context['usuarios_disponibles'] = User.objects.filter(
            models.Q(perfil__rol='profesional') | 
            models.Q(profesional__isnull=True)
        ).distinct()
        context['servicios_disponibles'] = Servicio.objects.filter(activo=True)
        return context


class ProfesionalAdminUpdateView(AdministradorRequiredMixin, UpdateView):
    """Vista para que administradores editen cualquier profesional"""
    model = Profesional
    template_name = 'usuarios/profesional_admin_editar.html'
    fields = [
        'nombre_completo', 'especialidad', 'telefono', 
        'email_profesional', 'numero_licencia', 'años_experiencia',
        'certificaciones', 'hora_inicio_disponibilidad', 
        'hora_fin_disponibilidad', 'dias_disponibles', 'biografia',
        'foto_profesional', 'servicios_que_ofrece', 'fecha_contratacion', 'activo'
    ]
    success_url = reverse_lazy('usuarios:profesional_gestion')
    
    def form_valid(self, form):
        """Procesar formulario válido"""
        messages.success(
            self.request, 
            f'Información de {form.instance.nombre_completo} actualizada exitosamente.'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profesional'] = self.object
        context['servicios_disponibles'] = Servicio.objects.filter(activo=True)
        return context


@login_required
def profesional_toggle_estado(request, pk):
    """Vista para cambiar el estado activo/inactivo de un profesional"""
    if not (hasattr(request.user, 'perfil') and request.user.perfil.rol == 'administrador'):
        messages.error(request, 'No tienes permisos para realizar esta acción.')
        return redirect('usuarios:profesional_gestion')
    
    profesional = get_object_or_404(Profesional, pk=pk)
    profesional.activo = not profesional.activo
    profesional.save()
    
    estado = "activado" if profesional.activo else "desactivado"
    messages.success(
        request, 
        f'Profesional {profesional.nombre_completo} {estado} exitosamente.'
    )
    
    return redirect('usuarios:profesional_gestion')


# =============================================================================
# VISTAS PARA GESTIÓN DE ESPECIALIDADES SECUNDARIAS
# =============================================================================

class EspecialidadSecundariaGestionView(AdministradorRequiredMixin, ListView):
    """Vista para gestión completa de especialidades secundarias por administradores"""
    model = EspecialidadSecundaria
    template_name = 'usuarios/especialidad_gestion.html'
    context_object_name = 'especialidades'
    paginate_by = 15
    
    def get_queryset(self):
        """Filtrar especialidades con opciones de búsqueda"""
        queryset = EspecialidadSecundaria.objects.select_related(
            'profesional_principal', 
            'profesional_especialidad'
        )
        
        # Filtros disponibles
        nivel = self.request.GET.get('nivel')
        if nivel:
            queryset = queryset.filter(nivel_competencia=nivel)
        
        busqueda = self.request.GET.get('buscar')
        if busqueda:
            queryset = queryset.filter(
                models.Q(profesional_principal__nombre_completo__icontains=busqueda) |
                models.Q(profesional_especialidad__nombre_completo__icontains=busqueda)
            )
        
        return queryset.order_by('profesional_principal__nombre_completo')
    
    def get_context_data(self, **kwargs):
        """Añadir estadísticas y datos de contexto"""
        context = super().get_context_data(**kwargs)
        
        # Estadísticas generales
        context['total_especialidades'] = EspecialidadSecundaria.objects.count()
        
        # Estadísticas por nivel
        niveles_stats = {}
        for codigo, nombre in EspecialidadSecundaria._meta.get_field('nivel_competencia').choices:
            count = EspecialidadSecundaria.objects.filter(nivel_competencia=codigo).count()
            if count > 0:
                niveles_stats[nombre] = count
        context['niveles_stats'] = niveles_stats
        
        # Opciones de filtrado
        context['niveles_choices'] = EspecialidadSecundaria._meta.get_field('nivel_competencia').choices
        context['nivel_actual'] = self.request.GET.get('nivel', '')
        context['busqueda_actual'] = self.request.GET.get('buscar', '')
        
        # Profesionales disponibles
        context['profesionales_disponibles'] = Profesional.objects.filter(activo=True)
        
        return context


class EspecialidadSecundariaCreateView(AdministradorRequiredMixin, CreateView):
    """Vista para crear nuevas especialidades secundarias"""
    model = EspecialidadSecundaria
    template_name = 'usuarios/especialidad_crear.html'
    fields = ['profesional_principal', 'profesional_especialidad', 'nivel_competencia']
    success_url = reverse_lazy('usuarios:especialidad_gestion')
    
    def form_valid(self, form):
        """Validar y crear especialidad secundaria"""
        # Verificar que no sea la misma persona
        if form.cleaned_data['profesional_principal'] == form.cleaned_data['profesional_especialidad']:
            messages.error(
                self.request, 
                'Un profesional no puede tener una especialidad secundaria de sí mismo.'
            )
            return self.form_invalid(form)
        
        messages.success(
            self.request, 
            f'Especialidad secundaria creada exitosamente para {form.cleaned_data["profesional_principal"].nombre_completo}'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profesionales'] = Profesional.objects.filter(activo=True).order_by('nombre_completo')
        return context


class EspecialidadSecundariaUpdateView(AdministradorRequiredMixin, UpdateView):
    """Vista para actualizar especialidades secundarias"""
    model = EspecialidadSecundaria
    template_name = 'usuarios/especialidad_editar.html'
    fields = ['profesional_principal', 'profesional_especialidad', 'nivel_competencia']
    success_url = reverse_lazy('usuarios:especialidad_gestion')
    
    def form_valid(self, form):
        """Validar y actualizar especialidad secundaria"""
        # Verificar que no sea la misma persona
        if form.cleaned_data['profesional_principal'] == form.cleaned_data['profesional_especialidad']:
            messages.error(
                self.request, 
                'Un profesional no puede tener una especialidad secundaria de sí mismo.'
            )
            return self.form_invalid(form)
        
        messages.success(
            self.request, 
            f'Especialidad secundaria actualizada exitosamente.'
        )
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profesionales'] = Profesional.objects.filter(activo=True).order_by('nombre_completo')
        context['especialidad'] = self.object
        return context


class EspecialidadSecundariaDeleteView(AdministradorRequiredMixin, DeleteView):
    """Vista para eliminar especialidades secundarias"""
    model = EspecialidadSecundaria
    template_name = 'usuarios/especialidad_confirm_delete.html'
    success_url = reverse_lazy('usuarios:especialidad_gestion')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Especialidad secundaria eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['especialidad'] = self.object
        return context
