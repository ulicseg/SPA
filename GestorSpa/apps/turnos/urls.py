from django.urls import path
from .views import (
    TurnoListView, 
    TurnoDetailView, 
    TurnoCreateView,
    TurnoUpdateView,
    TurnoDeleteView,
    TurnoConfirmacionView,
)

app_name = 'turnos'

urlpatterns = [
    # Rutas públicas
    path('reservar/', TurnoCreateView.as_view(), name='turno_create'),
    path('confirmacion/', TurnoConfirmacionView.as_view(), name='turno_confirmacion'),
    
    # Rutas administrativas
    path('admin/', TurnoListView.as_view(), name='turno_list'),
    path('admin/<int:pk>/', TurnoDetailView.as_view(), name='turno_detail'),
    path('admin/<int:pk>/editar/', TurnoUpdateView.as_view(), name='turno_update'),
    path('admin/<int:pk>/eliminar/', TurnoDeleteView.as_view(), name='turno_delete'),
] 