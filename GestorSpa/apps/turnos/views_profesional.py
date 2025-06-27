from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta
from .models import Turno
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from weasyprint import HTML
from django.template.loader import render_to_string

class TurnosDelProfesionalView(LoginRequiredMixin, ListView):
    model = Turno
    template_name = 'profesionales/turnos.html'
    context_object_name = 'turnos'

    def get_queryset(self):
        try:
            profesional = self.request.user.profesional
            return Turno.objects.filter(
                profesional=profesional,
                fecha=timezone.now().date() + timedelta(days=1),
                estado__in=['pendiente', 'confirmado']
            ).order_by('hora_inicio')
        except Exception:
            # Si no hay profesional asociado, devolver queryset vacío
            return Turno.objects.none()

class TurnosProfesionalPDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            profesional = request.user.profesional
            turnos = Turno.objects.filter(
                profesional=profesional,
                fecha=timezone.now().date() + timedelta(days=1),
                estado__in=['pendiente', 'confirmado']
            ).order_by('hora_inicio')
            
            html_string = render_to_string('profesionales/turnos_pdf.html', {
                'turnos': turnos, 
                'profesional': profesional
            })
            html = HTML(string=html_string)
            pdf = html.write_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="turnos_profesional.pdf"'
            return response
        except Exception as e:
            from django.shortcuts import redirect
            from django.contrib import messages
            messages.error(request, f'Error al generar PDF: {str(e)}')
            return redirect('usuarios:perfil')
