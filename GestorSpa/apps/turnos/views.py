from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from .models import Turno
from GestorSpa.apps.servicios.models import Servicio
from datetime import datetime, timedelta

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

class TurnoListView(AdminRequiredMixin, ListView):
    model = Turno
    template_name = 'turnos/turno_list.html'
    context_object_name = 'turnos'

    def get_queryset(self):
        return Turno.objects.all()

class TurnoDetailView(AdminRequiredMixin, DetailView):
    model = Turno
    template_name = 'turnos/turno_detail.html'
    context_object_name = 'turno'

    def get_queryset(self):
        return Turno.objects.all()

class TurnoCreateView(CreateView):
    model = Turno
    template_name = 'turnos/turno_form.html'
    fields = ['nombre', 'email', 'telefono', 'servicio', 'fecha', 'hora_inicio', 'notas']
    success_url = reverse_lazy('turnos:turno_confirmacion')

    def form_valid(self, form):
        servicio = form.cleaned_data['servicio']
        hora_inicio = form.cleaned_data['hora_inicio']
        duracion = servicio.duracion
        form.instance.hora_fin = (datetime.combine(datetime.today(), hora_inicio) + 
                                timedelta(minutes=duracion)).time()
        
        # Verificar si ya existe un turno para ese servicio en ese horario
        fecha = form.cleaned_data['fecha']
        turnos_existentes = Turno.objects.filter(
            servicio=servicio,
            fecha=fecha,
            hora_inicio=hora_inicio
        )
        
        if turnos_existentes.exists():
            messages.error(self.request, 'Ya existe un turno para este servicio en este horario.')
            return redirect('turnos:turno_create')
            
        response = super().form_valid(form)
        # Guardar el ID del turno en la sesión para la página de confirmación
        self.request.session['turno_id'] = self.object.id
        messages.success(self.request, 'Turno creado exitosamente.')
        return response

class TurnoConfirmacionView(TemplateView):
    template_name = 'turnos/turno_confirmacion.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        turno_id = self.request.session.get('turno_id')
        if turno_id:
            try:
                context['turno'] = get_object_or_404(Turno, id=turno_id)
                # Limpiamos el ID del turno de la sesión
                del self.request.session['turno_id']
            except Turno.DoesNotExist:
                messages.error(self.request, 'No se encontró el turno solicitado.')
        else:
            messages.warning(self.request, 'No hay un turno para confirmar.')
        return context

class TurnoUpdateView(AdminRequiredMixin, UpdateView):
    model = Turno
    template_name = 'turnos/turno_form.html'
    fields = ['nombre', 'email', 'telefono', 'servicio', 'fecha', 'hora_inicio', 'notas', 'estado']
    success_url = reverse_lazy('turnos:turno_list')

    def get_queryset(self):
        return Turno.objects.all()

    def form_valid(self, form):
        servicio = form.cleaned_data['servicio']
        hora_inicio = form.cleaned_data['hora_inicio']
        duracion = servicio.duracion
        form.instance.hora_fin = (datetime.combine(datetime.today(), hora_inicio) + 
                                timedelta(minutes=duracion)).time()
        
        # Verificar si ya existe un turno para ese servicio en ese horario
        fecha = form.cleaned_data['fecha']
        turnos_existentes = Turno.objects.filter(
            servicio=servicio,
            fecha=fecha,
            hora_inicio=hora_inicio
        ).exclude(pk=self.object.pk)
        
        if turnos_existentes.exists():
            messages.error(self.request, 'Ya existe un turno para este servicio en este horario.')
            return redirect('turnos:turno_update', pk=self.object.pk)
            
        messages.success(self.request, 'Turno actualizado exitosamente.')
        return super().form_valid(form)

class TurnoDeleteView(AdminRequiredMixin, DeleteView):
    model = Turno
    template_name = 'turnos/turno_confirm_delete.html'
    success_url = reverse_lazy('turnos:turno_list')

    def get_queryset(self):
        return Turno.objects.all()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Turno eliminado exitosamente.')
        return super().delete(request, *args, **kwargs) 