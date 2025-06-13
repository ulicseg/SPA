from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Vista principal unificada de perfil
    path('perfil/', views.perfil, name='perfil'),
    
    # Vista de prueba para admin
    path('test-perfil/', views.test_perfil, name='test_perfil'),
    
    # Gestión de usuarios
    path('gestionar/', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('asignar-rol/<int:user_id>/', views.asignar_rol_usuario, name='asignar_rol_usuario'),
    path('mis-turnos/', views.mis_turnos, name='mis_turnos'),
    path('registro-cliente/', views.ClienteRegistroView.as_view(), name='registro_cliente'),
    
    # URLs para profesionales
    path('profesional/', views.perfil_profesional, name='perfil_profesional'),
    path('profesional/editar-horarios/', views.editar_horarios_profesional, name='editar_horarios_profesional'),
    
    # URLs para administradores - gestión de profesionales
    path('profesionales/', views.gestionar_profesionales, name='gestionar_profesionales'),
    path('profesionales/<int:profesional_id>/', views.detalle_profesional, name='detalle_profesional'),
    path('profesionales/<int:profesional_id>/cambiar-estado/', views.cambiar_estado_profesional, name='cambiar_estado_profesional'),
    
    # API
    path('api/profesional/<int:profesional_id>/horarios/', views.api_horarios_profesional, name='api_horarios_profesional'),
]