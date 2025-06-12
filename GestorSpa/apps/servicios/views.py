from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Servicio
from .forms import ServicioForm
from GestorSpa.apps.usuarios.permissions import (
    AdministradorRequiredMixin,
    ProfesionalOrAdminRequiredMixin,
    administrador_required
)

class ServicioListView(ProfesionalOrAdminRequiredMixin, ListView):
    """Vista para listar servicios - Profesionales y administradores"""
    model = Servicio
    template_name = 'servicios/servicio_list.html'
    context_object_name = 'servicios'
    queryset = Servicio.objects.filter(activo=True)

class ServicioDetailView(DetailView):
    """Vista pública para ver detalles de servicio"""
    model = Servicio
    template_name = 'servicios/servicio_detail.html'
    context_object_name = 'servicio'
    
    def get_queryset(self):
        return Servicio.objects.filter(activo=True)

class ServicioCreateView(AdministradorRequiredMixin, CreateView):
    """Vista para crear servicios - Solo administradores"""
    model = Servicio
    form_class = ServicioForm
    template_name = 'servicios/servicio_form.html'
    success_url = reverse_lazy('servicios:servicio_list')

    def form_valid(self, form):
        form.instance.intervalo = 60
        return super().form_valid(form)

class ServicioUpdateView(AdministradorRequiredMixin, UpdateView):
    """Vista para editar servicios - Solo administradores"""
    model = Servicio
    form_class = ServicioForm
    template_name = 'servicios/servicio_form.html'
    success_url = reverse_lazy('servicios:servicio_list')

    def form_valid(self, form):
        form.instance.intervalo = 60
        return super().form_valid(form)

class ServicioDeleteView(AdministradorRequiredMixin, DeleteView):
    """Vista para eliminar servicios - Solo administradores"""
    model = Servicio
    template_name = 'servicios/servicio_confirm_delete.html'
    success_url = reverse_lazy('servicios:servicio_list')