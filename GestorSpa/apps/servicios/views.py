from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Servicio

class ServicioListView(ListView):
    model = Servicio
    template_name = 'servicios/servicio_list.html'
    context_object_name = 'servicios'
    queryset = Servicio.objects.filter(activo=True)

class ServicioDetailView(DetailView):
    model = Servicio
    template_name = 'servicios/servicio_detail.html'
    context_object_name = 'servicio'

class ServicioCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Servicio
    template_name = 'servicios/servicio_form.html'
    fields = ['nombre', 'descripcion', 'duracion', 'precio', 'imagen', 'activo']
    success_url = reverse_lazy('servicios:servicio_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Servicio creado exitosamente.')
        return super().form_valid(form)

class ServicioUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Servicio
    template_name = 'servicios/servicio_form.html'
    fields = ['nombre', 'descripcion', 'duracion', 'precio', 'imagen', 'activo']
    success_url = reverse_lazy('servicios:servicio_list')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Servicio actualizado exitosamente.')
        return super().form_valid(form)

class ServicioDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Servicio
    template_name = 'servicios/servicio_confirm_delete.html'
    success_url = reverse_lazy('servicios:servicio_list')

    def test_func(self):
        return self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Servicio eliminado exitosamente.')
        return super().delete(request, *args, **kwargs) 