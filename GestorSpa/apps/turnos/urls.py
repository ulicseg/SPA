from django.urls import path
from . import views
from . import views_profesional
from .views_with_permissions import reporte_turnos

app_name = 'turnos'

urlpatterns = [
    path('', views.TurnoListView.as_view(), name='turno_list'),
    path('editar/<int:pk>/', views.TurnoUpdateView.as_view(), name='turno_update'),
    path('eliminar/<int:pk>/', views.TurnoDeleteView.as_view(), name='turno_delete'),
    path('calendario/', views.calendario_disponibilidad, name='calendario_disponibilidad'),
    path('verificar-disponibilidad/', views.verificar_disponibilidad, name='verificar_disponibilidad'),
    path('reservar/', views.TurnoReservaUnificadaView.as_view(), name='turno_reserva_unificada'),
    path('confirmacion/', views.TurnoConfirmacionView.as_view(), name='turno_confirmacion'),
    path('pdf/<int:pk>/', views.turno_pdf, name='turno_pdf'),
    path('profesional/turnos-manana/', views_profesional.TurnosDelProfesionalView.as_view(), name='turnos_profesional_manana'),
    path('profesional/turnos-manana/pdf/', views_profesional.TurnosProfesionalPDFView.as_view(), name='turnos_profesional_pdf'),
    path('reporte/', reporte_turnos, name='reporte_turnos'),
    path('api/servicio/<int:servicio_id>/profesionales/', views.api_profesionales_por_servicio, name='api_profesionales_por_servicio'),
]