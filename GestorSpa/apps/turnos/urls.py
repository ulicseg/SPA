from django.urls import path
from . import views

app_name = 'turnos'

urlpatterns = [
    path('', views.TurnoListView.as_view(), name='turno_list'),
    path('nuevo/', views.TurnoCreateView.as_view(), name='turno_create'),
    path('editar/<int:pk>/', views.TurnoUpdateView.as_view(), name='turno_update'),
    path('eliminar/<int:pk>/', views.TurnoDeleteView.as_view(), name='turno_delete'),
    path('calendario/', views.calendario_disponibilidad, name='calendario_disponibilidad'),
    path('verificar-disponibilidad/', views.verificar_disponibilidad, name='verificar_disponibilidad'),
    path('reservar/', views.TurnoReservaUnificadaView.as_view(), name='turno_reserva_unificada'),
    path('confirmacion/', views.TurnoConfirmacionView.as_view(), name='turno_confirmacion'),
] 