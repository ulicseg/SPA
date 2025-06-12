# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from .models import Turno
from GestorSpa.apps.servicios.models import Servicio
from GestorSpa.apps.usuarios.permissions import (
    RoleManager, 
    AdministradorRequiredMixin, 
    ClienteOrAdminRequiredMixin,
    ProfesionalOrAdminRequiredMixin,
    role_required,
    administrador_required,
    cliente_or_admin_required,
    profesional_or_admin_required
)
from GestorSpa.apps.usuarios.models import Profesional
from datetime import datetime, timedelta, date
from calendar import monthcalendar, month_name
import locale
from .forms import TurnoForm
from django.views.decorators.http import require_http_methods
from weasyprint import HTML
from django.template.loader import render_to_string
import os
import logging

# Configurar logger para debugging
logger = logging.getLogger(__name__)

# Configurar locale para español
try:
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Spanish_Spain.1252')
    except:
        pass

class CalendarioDisponibilidadView(TemplateView):
    """Vista pública para mostrar calendario de disponibilidad"""
    template_name = 'turnos/calendario_disponibilidad.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['servicios'] = Servicio.objects.filter(activo=True)
        return context


class HorariosDisponiblesDiaView(TemplateView):
    """Vista pública para mostrar horarios disponibles de un día"""
    template_name = 'turnos/horarios_disponibles_dia.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obtener parámetros
        fecha_str = self.request.GET.get('fecha')
        servicio_id = self.request.GET.get('servicio')
        
        if not fecha_str or not servicio_id:
            messages.error(self.request, 'Faltan parámetros requeridos')
            return context
        
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            servicio = Servicio.objects.get(id=servicio_id)
            
            # Obtener horarios disponibles
            horarios_disponibles = Turno.get_horarios_disponibles(fecha, servicio)
            
            # Obtener turnos existentes para este día
            turnos_existentes = Turno.objects.filter(
                fecha=fecha,
                servicio=servicio,
                estado__in=['pendiente', 'confirmado']
            ).order_by('hora_inicio')
            
            context['fecha'] = fecha
            context['servicio'] = servicio
            context['horarios_disponibles'] = horarios_disponibles
            context['turnos_existentes'] = turnos_existentes
            
        except (ValueError, Servicio.DoesNotExist) as e:
            messages.error(self.request, str(e))
        
        return context

class TurnoListView(ProfesionalOrAdminRequiredMixin, ListView):
    """Vista para listar turnos - Solo profesionales y administradores"""
    model = Turno
    template_name = 'turnos/turno_list.html'
    context_object_name = 'turnos'
    ordering = ['fecha', 'hora_inicio']

    def get_queryset(self):
        queryset = Turno.objects.all()
        
        # Si es profesional, solo ve sus propios turnos
        user_role = RoleManager.get_user_role(self.request.user)
        if user_role == 'profesional':
            # Aquí podrías filtrar por profesional asignado si tienes ese campo
            # queryset = queryset.filter(profesional=self.request.user)
            pass
        
        fecha_filtro = self.request.GET.get('fecha')
        if fecha_filtro:
            try:
                fecha = datetime.strptime(fecha_filtro, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha=fecha)
            except ValueError:
                pass
                
        return queryset.order_by('fecha', 'hora_inicio')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['fecha_filtro'] = self.request.GET.get('fecha', '')
        return context

class TurnoDetailView(ProfesionalOrAdminRequiredMixin, DetailView):
    """Vista para ver detalles de turno - Solo profesionales y administradores"""
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

def calendario_disponibilidad(request):
    """Vista pública para calendario de disponibilidad"""
    servicios = Servicio.objects.filter(activo=True)
    return render(request, 'turnos/calendario_disponibilidad.html', {
        'servicios': servicios
    })

class TurnoUpdateView(AdministradorRequiredMixin, UpdateView):
    """Vista para editar turnos - Solo administradores"""
    model = Turno
    form_class = TurnoForm
    template_name = 'turnos/turno_form.html'
    success_url = reverse_lazy('turnos:turno_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['servicios'] = Servicio.objects.filter(activo=True)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Turno actualizado exitosamente.')
        return super().form_valid(form)

class TurnoDeleteView(AdministradorRequiredMixin, DeleteView):
    """Vista para eliminar turnos - Solo administradores"""
    model = Turno
    template_name = 'turnos/turno_confirm_delete.html'
    success_url = reverse_lazy('turnos:turno_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Turno eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

class TurnoDeleteView(LoginRequiredMixin, DeleteView):
    model = Turno
    template_name = 'turnos/turno_confirm_delete.html'
    success_url = reverse_lazy('turnos:turno_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Turno eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

@require_http_methods(["GET"])
def verificar_disponibilidad(request):
    fecha = request.GET.get('fecha')
    servicio_id = request.GET.get('servicio')
    profesional_id = request.GET.get('profesional')
    if not fecha or not servicio_id or not profesional_id:
        return JsonResponse({'error': 'Fecha, servicio y profesional son requeridos'}, status=400)
    try:
        fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
        from GestorSpa.apps.servicios.models import Servicio
        from GestorSpa.apps.usuarios.models import Profesional
        servicio = Servicio.objects.get(pk=servicio_id)
        profesional = Profesional.objects.get(pk=profesional_id)
        # Usar lógica del formulario para obtener horarios disponibles
        from .forms import TurnoForm
        horarios = TurnoForm().get_horarios_disponibles(fecha_dt, servicio, profesional)
        return JsonResponse({'horarios_disponibles': horarios})
    except Servicio.DoesNotExist:
        return JsonResponse({'error': 'Servicio no encontrado'}, status=404)
    except Profesional.DoesNotExist:
        return JsonResponse({'error': 'Profesional no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_horarios_disponibles(request):
    fecha = request.GET.get('fecha')
    servicio_id = request.GET.get('servicio_id')
    
    if not fecha or not servicio_id:
        return JsonResponse({'error': 'Fecha y servicio son requeridos'}, status=400)
    
    try:
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        servicio = get_object_or_404(Servicio, id=servicio_id)
        
        # Generar horarios disponibles
        horarios_disponibles = []
        hora_inicio = timezone.datetime.combine(fecha, timezone.datetime.min.time().replace(hour=9))  # 9 AM
        hora_fin = timezone.datetime.combine(fecha, timezone.datetime.min.time().replace(hour=18))    # 6 PM
        
        while hora_inicio < hora_fin:
            # Verificar si ya existe un turno para esta hora
            turno_existente = Turno.objects.filter(
                fecha=fecha,
                hora_inicio=hora_inicio.time(),
                servicio=servicio
            ).exists()
            
            if not turno_existente:
                horarios_disponibles.append({
                    'hora': hora_inicio.strftime('%H:%M'),
                    'disponible': True
                })
            
            hora_inicio += timedelta(minutes=30)  # Intervalos de 30 minutos
        
        return JsonResponse({'horarios': horarios_disponibles})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

class TurnoConfirmacionView(TemplateView):
    template_name = 'turnos/turno_confirmacion.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        turno_id = self.request.session.get('turno_id')
        if turno_id:
            try:
                context['turno'] = get_object_or_404(Turno, id=turno_id)
                del self.request.session['turno_id']
            except Turno.DoesNotExist:
                messages.error(self.request, 'No se encontró el turno solicitado.')
        else:
            # Si no hay turno_id en la sesión, intentar obtener el último turno creado
            try:
                context['turno'] = Turno.objects.order_by('-created_at').first()
            except Turno.DoesNotExist:
                messages.warning(self.request, 'No hay un turno para confirmar.')
        return context

def turno_confirmacion(request):
    return render(request, 'turnos/turno_confirmacion.html')

from django.contrib.auth.mixins import LoginRequiredMixin

# ...existing code...

class TurnoReservaUnificadaView(LoginRequiredMixin, TemplateView):
    template_name = 'turnos/turno_reserva_unificada.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Redirigir usuarios no autenticados al registro con mensaje claro"""
        if not request.user.is_authenticated:
            messages.info(
                request, 
                '🔐 Para reservar un turno en nuestro SPA necesitas estar registrado. '
                '¡Es gratis y rápido! Regístrate como cliente para comenzar.'
            )
            return redirect('usuarios:registro_cliente')
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['servicios'] = Servicio.objects.all()
        
        # Pre-llenar formulario con datos del usuario
        initial_data = {
            'nombre': f"{self.request.user.first_name} {self.request.user.last_name}".strip() or self.request.user.username,
            'email': self.request.user.email,
        }
        context['form'] = TurnoForm(initial=initial_data)
        return context
        
    def post(self, request, *args, **kwargs):
        """Procesa la reserva con manejo robusto de encoding UTF-8"""
        try:
            # Configurar encoding para la request
            if hasattr(request, 'encoding'):
                request.encoding = 'utf-8'
            
            form = TurnoForm(request.POST)
            if form.is_valid():
                try:
                    turno = form.save(commit=False)
                    # Siempre asociar con el usuario logueado
                    turno.usuario = request.user
                    # Asegurar que el email sea el del usuario
                    turno.email = request.user.email
                    # Asegurar que el nombre sea el del usuario
                    if not turno.nombre.strip():
                        turno.nombre = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
                    turno.save()
                    # Guardar el ID del turno en la sesión
                    request.session['turno_id'] = turno.id
                    logger.info(f"Turno creado exitosamente: {turno.id}")
                    return redirect('turnos:turno_confirmacion')
                except UnicodeEncodeError as e:
                    logger.error(f"Error de encoding al guardar turno: {str(e)}")
                    messages.error(request, 'Error de codificación de caracteres. Verifique que no haya caracteres especiales en los datos.')
                except Exception as e:
                    logger.error(f"Error general al guardar turno: {str(e)}")
                    messages.error(request, f'Error al procesar la reserva: {str(e)}')
            else:
                # Manejar errores del formulario con encoding seguro
                for field, errors in form.errors.items():
                    for error in errors:
                        try:
                            # Asegurar que el mensaje sea UTF-8
                            error_msg = str(error).encode('utf-8', errors='ignore').decode('utf-8')
                            field_name = str(field).encode('utf-8', errors='ignore').decode('utf-8')
                            messages.error(request, f'Error en {field_name}: {error_msg}')
                        except (UnicodeEncodeError, UnicodeDecodeError):
                            messages.error(request, f'Error en {field}: Error de caracteres especiales')
            
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)
            
        except UnicodeEncodeError as e:
            logger.error(f"Error de encoding en POST: {str(e)}")
            messages.error(request, 'Error de codificación de caracteres. Por favor, evite usar caracteres especiales.')
            context = self.get_context_data()
            form = TurnoForm(request.POST)
            context['form'] = form
            return self.render_to_response(context)
        except Exception as e:
            logger.error(f"Error general en POST: {str(e)}")
            try:
                error_msg = str(e).encode('utf-8', errors='ignore').decode('utf-8')
                messages.error(request, f'Error al procesar la reserva: {error_msg}')
            except (UnicodeEncodeError, UnicodeDecodeError):
                messages.error(request, 'Error al procesar la reserva: Error de caracteres especiales')
            context = self.get_context_data()
            form = TurnoForm(request.POST)
            context['form'] = form
            return self.render_to_response(context)

def turno_pdf(request, pk):
    turno = get_object_or_404(Turno, pk=pk)
    
    # Si el usuario no está autenticado, verificar si el turno fue creado recientemente
    if not request.user.is_authenticated:
        # Verificar si el turno fue creado recientemente (en los últimos 5 minutos)
        if (timezone.now() - turno.created_at).total_seconds() > 300:  # 300 segundos = 5 minutos
            messages.error(request, 'No tiene permiso para acceder a este recurso.')
            return redirect('home')
    
    # Renderizar el template HTML
    html_string = render_to_string('turnos/turno_pdf.html', {
        'turno': turno,
        'base_url': request.build_absolute_uri('/')[:-1]
    })
    
    # Generar el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="turno_{turno.id}.pdf"'
    
    # Generar el PDF usando WeasyPrint
    HTML(string=html_string).write_pdf(response)
    
    return response

def api_profesionales_por_servicio(request, servicio_id):
    """Devuelve los profesionales habilitados para un servicio (API)."""
    from GestorSpa.apps.usuarios.models import Profesional
    try:
        profesionales = Profesional.objects.filter(
            servicios_especialidad=servicio_id,
            estado='activo'
        )
        data = []
        for p in profesionales:
            try:
                nombre = str(p)
            except UnicodeEncodeError:
                nombre = p.nombre_completo if hasattr(p, 'nombre_completo') else f'Profesional {p.id}'
            data.append({'id': p.id, 'nombre': nombre})
        return JsonResponse(data, safe=False)
    except Exception as e:
        try:
            error_msg = str(e)
        except UnicodeEncodeError:
            error_msg = 'Error de caracteres especiales'
        return JsonResponse({'error': error_msg}, status=500)


class TurnoDetailView(LoginRequiredMixin, DetailView):
    """Vista de detalle para visualizar información completa de un turno"""    
    model = Turno
    template_name = 'turnos/turno_detail.html'
    context_object_name = 'turno'
    
    def get_queryset(self):
        """Filtrar turnos según el rol del usuario"""
        user = self.request.user
        role_manager = RoleManager()
        
        # Administradores pueden ver todos los turnos
        if role_manager.user_has_role(user, 'administrador'):
            return Turno.objects.select_related('servicio', 'profesional', 'usuario').all()
        
        # Profesionales pueden ver sus turnos asignados
        elif role_manager.user_has_role(user, 'profesional'):
            return Turno.objects.select_related('servicio', 'profesional', 'usuario').filter(
                profesional__user=user
            )
        
        # Clientes solo pueden ver sus propios turnos        else:
            return Turno.objects.select_related('servicio', 'profesional', 'usuario').filter(
                usuario=user
            )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_role'] = RoleManager.get_user_role(self.request.user)
        return context