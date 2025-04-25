from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Turno
from GestorSpa.apps.servicios.models import Servicio
from datetime import datetime, timedelta, date
from calendar import monthcalendar, month_name
import locale
from .forms import TurnoForm
from django.views.decorators.http import require_http_methods

# Configurar locale para español
try:
    locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Spanish_Spain.1252')
    except:
        pass

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

class CalendarioDisponibilidadView(TemplateView):
    template_name = 'turnos/calendario_disponibilidad.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['servicios'] = Servicio.objects.all()
        return context

class HorariosDisponiblesDiaView(TemplateView):
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

class TurnoListView(LoginRequiredMixin, ListView):
    model = Turno
    template_name = 'turnos/turno_list.html'
    context_object_name = 'turnos'
    ordering = ['fecha', 'hora_inicio']

    def get_queryset(self):
        queryset = Turno.objects.all()
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

class TurnoDetailView(AdminRequiredMixin, DetailView):
    model = Turno
    template_name = 'turnos/turno_detail.html'
    context_object_name = 'turno'

    def get_queryset(self):
        return Turno.objects.all()

def calendario_disponibilidad(request):
    servicios = Servicio.objects.all()
    return render(request, 'turnos/calendario_disponibilidad.html', {
        'servicios': servicios
    })

class TurnoCreateView(CreateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'turnos/turno_form.html'
    success_url = reverse_lazy('turnos:turno_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['servicios'] = Servicio.objects.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Turno creado exitosamente.')
        return super().form_valid(form)

class TurnoUpdateView(LoginRequiredMixin, UpdateView):
    model = Turno
    form_class = TurnoForm
    template_name = 'turnos/turno_form.html'
    success_url = reverse_lazy('turnos:turno_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['servicios'] = Servicio.objects.all()
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Turno actualizado exitosamente.')
        return super().form_valid(form)

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
    hora_inicio_str = request.GET.get('hora_inicio', '09:00')
    hora_fin_str = request.GET.get('hora_fin', '20:00')

    if not fecha or not servicio_id:
        return JsonResponse({
            'error': 'Se requieren los parámetros fecha y servicio'
        }, status=400)

    try:
        servicio = Servicio.objects.get(id=servicio_id)
        fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        
        # Convertir las horas de string a time
        hora_inicio = datetime.strptime(hora_inicio_str, '%H:%M').time()
        hora_fin = datetime.strptime(hora_fin_str, '%H:%M').time()
        
        # Actualizar temporalmente los horarios del servicio
        servicio.hora_inicio = hora_inicio
        servicio.hora_fin = hora_fin
        
        horarios_disponibles = Turno.get_horarios_disponibles(fecha, servicio)
        
        return JsonResponse({
            'horarios_disponibles': horarios_disponibles
        })
    except Servicio.DoesNotExist:
        return JsonResponse({
            'error': 'Servicio no encontrado'
        }, status=404)
    except ValueError:
        return JsonResponse({
            'error': 'Formato de fecha inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

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

class TurnoReservaUnificadaView(TemplateView):
    template_name = 'turnos/turno_reserva_unificada.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['servicios'] = Servicio.objects.all()
        context['form'] = TurnoForm()
        return context
        
    def post(self, request, *args, **kwargs):
        try:
            form = TurnoForm(request.POST)
            if form.is_valid():
                turno = form.save()
                # Guardar el ID del turno en la sesión
                request.session['turno_id'] = turno.id
                return redirect('turnos:turno_confirmacion')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Error en {field}: {error}')
                context = self.get_context_data()
                context['form'] = form
                return self.render_to_response(context)
        except Exception as e:
            messages.error(request, f'Error al procesar la reserva: {str(e)}')
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context) 