from django.urls import path
from .views import (
    TurnoListView, 
    TurnoDetailView, 
    TurnoCreateView,
    TurnoUpdateView,
    TurnoDeleteView,
)

app_name = 'turnos'

urlpatterns = [
    path('', TurnoListView.as_view(), name='turno_list'),
    path('nuevo/', TurnoCreateView.as_view(), name='turno_create'),
    path('<int:pk>/', TurnoDetailView.as_view(), name='turno_detail'),
    path('<int:pk>/editar/', TurnoUpdateView.as_view(), name='turno_update'),
    path('<int:pk>/eliminar/', TurnoDeleteView.as_view(), name='turno_delete'),
] 