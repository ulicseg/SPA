from GestorSpa.apps.usuarios.permissions import (
    AdministradorRequiredMixin, ClienteOrAdminRequiredMixin, ProfesionalOrAdminRequiredMixin, profesional_or_admin_required, administrador_required, RoleManager
)
from django.views.generic import DetailView, CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from .forms import TurnoForm
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime
from .models import Turno
from GestorSpa.apps.servicios.models import Servicio
from GestorSpa.apps.usuarios.permissions import cliente_or_admin_required

# Agregando las importaciones y actualizaciones de permisos al archivo de vistas de turnos

# Las siguientes clases reemplazan las existentes con controles de permisos por roles:

# TurnoDetailView - Solo administradores y profesionales pueden ver detalles
class TurnoDetailViewWithPermissions(ProfesionalOrAdminRequiredMixin, DetailView):
    model = Turno
    template_name = 'turnos/turno_detail.html'
    context_object_name = 'turno'

    def get_queryset(self):
        queryset = Turno.objects.all()
        user_role = RoleManager.get_user_role(self.request.user)
        
        # Si es profesional, solo puede ver sus propios turnos
        if user_role == 'profesional':
            # Filtrar por profesional asignado cuando tengas ese campo
            # queryset = queryset.filter(profesional=self.request.user)
            pass
            
        return queryset


# TurnoCreateView - Solo clientes y administradores pueden crear turnos
class TurnoCreateViewWithPermissions(ClienteOrAdminRequiredMixin, CreateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'turnos/turno_form.html'
    success_url = reverse_lazy('turnos:turno_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['servicios'] = Servicio.objects.filter(activo=True)
        return context

    def form_valid(self, form):
        # Si es cliente, asignar automáticamente sus datos
        user_role = RoleManager.get_user_role(self.request.user)
        if user_role == 'cliente':
            form.instance.nombre = f"{self.request.user.first_name} {self.request.user.last_name}".strip()
            form.instance.email = self.request.user.email
            if hasattr(self.request.user, 'perfil') and self.request.user.perfil.telefono:
                form.instance.telefono = self.request.user.perfil.telefono
        
        messages.success(self.request, 'Turno creado exitosamente.')
        return super().form_valid(form)


# TurnoUpdateView - Solo administradores pueden editar turnos
class TurnoUpdateViewWithPermissions(AdministradorRequiredMixin, UpdateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'turnos/turno_form.html'
    success_url = reverse_lazy('turnos:turno_list')

    def form_valid(self, form):
        messages.success(self.request, 'Turno actualizado exitosamente.')
        return super().form_valid(form)


# TurnoDeleteView - Solo administradores pueden eliminar turnos
class TurnoDeleteViewWithPermissions(AdministradorRequiredMixin, DeleteView):
    model = Turno
    template_name = 'turnos/turno_confirm_delete.html'
    success_url = reverse_lazy('turnos:turno_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Turno eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)


# Vista para que los clientes vean sus propios turnos
class MisTurnosView(ClienteOrAdminRequiredMixin, ListView):
    model = Turno
    template_name = 'turnos/mis_turnos.html'
    context_object_name = 'turnos'
    
    def get_queryset(self):
        # Los clientes solo ven sus propios turnos
        user_role = RoleManager.get_user_role(self.request.user)
        if user_role == 'cliente':
            return Turno.objects.filter(
                email=self.request.user.email
            ).order_by('-fecha', '-hora_inicio')
        else:
            # Los administradores ven todos
            return Turno.objects.all().order_by('-fecha', '-hora_inicio')


# Funciones con decoradores para vistas basadas en funciones

@cliente_or_admin_required
def verificar_disponibilidad_with_permissions(request):
    fecha_str = request.GET.get('fecha')
    servicio_id = request.GET.get('servicio')
    
    if not fecha_str or not servicio_id:
        return JsonResponse({'error': 'Parámetros faltantes'}, status=400)
    
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        servicio = Servicio.objects.get(id=servicio_id, activo=True)
        
        horarios_disponibles = Turno.get_horarios_disponibles(fecha, servicio)
        
        return JsonResponse({
            'horarios_disponibles': horarios_disponibles,
            'fecha': fecha_str,
            'servicio': servicio.nombre
        })
        
    except (ValueError, Servicio.DoesNotExist) as e:
        return JsonResponse({'error': str(e)}, status=400)


@administrador_required
def reporte_turnos(request):
    """Vista para generar reportes - Solo administradores"""
    from django.db.models import Count
    from django.utils import timezone
    from django.db.models import Sum
    from django.http import HttpResponse
    import csv
    from weasyprint import HTML
    from django.template.loader import render_to_string
    from .models import Turno
    from GestorSpa.apps.servicios.models import Servicio
    from GestorSpa.apps.usuarios.permissions import (
        administrador_required
    )
    
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    export = request.GET.get('export')
    turnos = Turno.objects.all()
    if fecha_inicio and fecha_fin:
        turnos = turnos.filter(fecha__range=[fecha_inicio, fecha_fin])
    # Totales por servicio
    totales_servicio = turnos.values('servicio__nombre').annotate(
        cantidad=Count('id'),
        total_pagado=Sum('total')
    )
    # Totales por profesional
    totales_profesional = turnos.values('profesional__nombre_completo').annotate(
        cantidad=Count('id'),
        total_pagado=Sum('total')
    )
    if export == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="reporte_turnos.csv"'
        writer = csv.writer(response)
        writer.writerow(['Fecha', 'Hora', 'Servicio', 'Profesional', 'Cliente', 'Método de Pago', 'Total', 'Estado'])
        for t in turnos:
            writer.writerow([
                t.fecha, t.hora_inicio, t.servicio.nombre, t.profesional,
                t.nombre, t.get_metodo_pago_display(), t.total, t.get_estado_display()
            ])
        return response
    if export == 'pdf':
        html_string = render_to_string('turnos/reporte_turnos.html', {
            'turnos': turnos,
            'totales_servicio': totales_servicio,
            'totales_profesional': totales_profesional,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin
        })
        html = HTML(string=html_string)
        pdf = html.write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_turnos.pdf"'
        return response
    context = {
        'turnos': turnos,
        'totales_servicio': totales_servicio,
        'totales_profesional': totales_profesional,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin
    }
    
    # Estadísticas básicas
    total_turnos = Turno.objects.count()
    turnos_hoy = Turno.objects.filter(fecha=timezone.now().date()).count()
    turnos_pendientes = Turno.objects.filter(estado='pendiente').count()
    turnos_completados = Turno.objects.filter(estado='completado').count()
    
    # Turnos por estado
    turnos_por_estado = Turno.objects.values('estado').annotate(
        total=Count('id')
    )
    
    context.update({
        'total_turnos': total_turnos,
        'turnos_hoy': turnos_hoy,
        'turnos_pendientes': turnos_pendientes,
        'turnos_completados': turnos_completados,
        'turnos_por_estado': turnos_por_estado,
    })
    
    return render(request, 'turnos/reporte_turnos.html', context)


@profesional_or_admin_required
def calendario_profesional(request):
    """Vista de calendario para profesionales"""
    user_role = RoleManager.get_user_role(request.user)
    
    if user_role == 'profesional':
        # Filtrar turnos del profesional
        turnos = Turno.objects.filter(
            # profesional=request.user,  # Cuando tengas este campo
            estado__in=['pendiente', 'confirmado']
        )
    else:
        # Administradores ven todos los turnos
        turnos = Turno.objects.filter(estado__in=['pendiente', 'confirmado'])
    
    context = {
        'turnos': turnos,
        'is_profesional': user_role == 'profesional'
    }
    
    return render(request, 'turnos/calendario_profesional.html', context)


# Función para cambiar estado de turno - Solo profesionales y administradores
@profesional_or_admin_required
def cambiar_estado_turno(request, turno_id):
    turno = get_object_or_404(Turno, id=turno_id)
    nuevo_estado = request.POST.get('estado')
    
    if nuevo_estado in ['pendiente', 'confirmado', 'cancelado', 'completado']:
        turno.estado = nuevo_estado
        turno.save()
        messages.success(request, f'Estado del turno cambiado a: {turno.get_estado_display()}')
    else:
        messages.error(request, 'Estado inválido.')
    
    return redirect('turnos:turno_detail', pk=turno.id)
