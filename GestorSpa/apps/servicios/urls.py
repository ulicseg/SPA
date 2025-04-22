from django.urls import path
from . import views

app_name = 'servicios'

urlpatterns = [
    path('', views.ServicioListView.as_view(), name='servicio_list'),
    path('<int:pk>/', views.ServicioDetailView.as_view(), name='servicio_detail'),
    path('crear/', views.ServicioCreateView.as_view(), name='servicio_create'),
    path('<int:pk>/editar/', views.ServicioUpdateView.as_view(), name='servicio_update'),
    path('<int:pk>/eliminar/', views.ServicioDeleteView.as_view(), name='servicio_delete'),
] 