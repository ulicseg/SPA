from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [    # Vista principal unificada de perfil
    path('perfil/', views.perfil, name='perfil'),
      # Gestión de usuarios
    path('gestionar/', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('eliminar/<int:user_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('mis-turnos/', views.mis_turnos, name='mis_turnos'),
    path('registro-cliente/', views.ClienteRegistroView.as_view(), name='registro_cliente'),    # URLs para profesionales
    path('profesional/editar-horarios/', views.editar_horarios_profesional, name='editar_horarios_profesional'),
    path('profesional/marcar-completado/<int:turno_id>/', views.marcar_turno_completado, name='marcar_turno_completado'),
      # URLs para administradores - gestión de profesionales
    path('profesionales/', views.gestionar_profesionales, name='gestionar_profesionales'),
    path('profesionales/crear/', views.crear_profesional, name='crear_profesional'),
    path('profesionales/<int:profesional_id>/', views.detalle_profesional, name='detalle_profesional'),
    path('profesionales/<int:profesional_id>/cambiar-estado/', views.cambiar_estado_profesional, name='cambiar_estado_profesional'),
    
    # Gestión de turnos por administradores
    path('cambiar-estado-turno/<int:turno_id>/', views.cambiar_estado_turno, name='cambiar_estado_turno'),
    path('autocompletar-turnos/', views.ejecutar_autocompletado_turnos, name='autocompletar_turnos'),

    # API
    path('api/profesional/<int:profesional_id>/horarios/', views.api_horarios_profesional, name='api_horarios_profesional'),
]