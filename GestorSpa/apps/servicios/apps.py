from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ServiciosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'GestorSpa.apps.servicios'
    verbose_name = _('Gestión de Servicios') 