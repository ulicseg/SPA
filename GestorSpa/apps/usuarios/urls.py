from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('perfil/', views.perfil, name='perfil'),
    path('perfil/editar/', views.PerfilUpdateView.as_view(), name='perfil_update'),
    path('dashboard/', views.dashboard_rol, name='dashboard_rol'),
    path('usuarios/', views.UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/<int:pk>/rol/', views.AsignarRolView.as_view(), name='asignar_rol'),
    
    # URLs específicas para profesionales
    path('profesional/perfil/', views.perfil_profesional, name='perfil_profesional'),
    path('profesional/editar/', views.ProfesionalUpdateView.as_view(), name='profesional_editar'),
    path('profesionales/', views.ProfesionalListView.as_view(), name='profesional_lista'),
    path('profesionales/<int:pk>/', views.ProfesionalDetailView.as_view(), name='profesional_detalle'),
      # URLs para gestión de profesionales (solo administradores)
    path('profesionales/gestion/', views.ProfesionalGestionView.as_view(), name='profesional_gestion'),
    path('profesionales/crear/', views.ProfesionalCreateView.as_view(), name='profesional_crear'),
    path('profesionales/<int:pk>/editar/', views.ProfesionalAdminUpdateView.as_view(), name='profesional_admin_editar'),
    path('profesionales/<int:pk>/toggle-estado/', views.profesional_toggle_estado, name='profesional_toggle_estado'),
    
    # URLs para gestión de especialidades secundarias (solo administradores)
    path('especialidades/gestion/', views.EspecialidadSecundariaGestionView.as_view(), name='especialidad_gestion'),
    path('especialidades/crear/', views.EspecialidadSecundariaCreateView.as_view(), name='especialidad_crear'),
    path('especialidades/<int:pk>/editar/', views.EspecialidadSecundariaUpdateView.as_view(), name='especialidad_editar'),
    path('especialidades/<int:pk>/eliminar/', views.EspecialidadSecundariaDeleteView.as_view(), name='especialidad_eliminar'),
    
    # AJAX URLs
    path('ajax/profesionales-por-servicio/', views.ajax_profesionales_por_servicio, name='ajax_profesionales_por_servicio'),
]