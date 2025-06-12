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
        return Turno.objects.filter(
            profesional=self.request.user.profesional,
            fecha=timezone.now().date() + timedelta(days=1),
            estado__in=['pendiente', 'confirmado']
        ).order_by('hora_inicio')

class TurnosProfesionalPDFView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        turnos = Turno.objects.filter(
            profesional=request.user.profesional,
            fecha=timezone.now().date() + timedelta(days=1),
            estado__in=['pendiente', 'confirmado']
        ).order_by('hora_inicio')
        html_string = render_to_string('profesionales/turnos_pdf.html', {'turnos': turnos, 'profesional': request.user.profesional})
        html = HTML(string=html_string)
        pdf = html.write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="turnos_profesional.pdf"'
        return response
