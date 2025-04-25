from django.db import models
from django.utils.translation import gettext_lazy as _

class Servicio(models.Model):
    ICON_CHOICES = [
        ('fa-solid fa-hands', 'Masaje General'),
        ('fa-solid fa-hot-tub-person', 'Sauna'),
        ('fa-solid fa-face-smile', 'Facial'),
        ('fa-solid fa-spray-can-sparkles', 'Aromaterapia'),
        ('fa-solid fa-droplet', 'Hidroterapia'),
        ('fa-solid fa-spa', 'Spa'),
        ('fa-solid fa-heart', 'Bienestar'),
        ('fa-solid fa-wind', 'Relajación'),
        ('fa-solid fa-massage', 'Masaje Específico'),
        ('fa-solid fa-bottle-droplet', 'Aceites Esenciales'),
        ('fa-solid fa-hand-holding-heart', 'Cuidado Personal'),
        ('fa-solid fa-cloud', 'Vapor'),
    ]

    nombre = models.CharField(_('Nombre del servicio'), max_length=100)
    descripcion = models.TextField(_('Descripción'))
    duracion = models.IntegerField(_('Duración en minutos'), help_text="Duración en minutos")
    precio = models.DecimalField(_('Precio'), max_digits=10, decimal_places=2)
    imagen = models.ImageField(_('Imagen del servicio'), upload_to='servicios/', null=True, blank=True)
    icono = models.CharField(_('Ícono'), max_length=50, choices=ICON_CHOICES, default='fa-solid fa-spa')
    hora_inicio = models.TimeField(default='09:00', help_text="Hora de inicio de atención")
    hora_fin = models.TimeField(default='20:00', help_text="Hora de fin de atención")
    intervalo = models.IntegerField(default=60, help_text="Intervalo entre turnos en minutos")
    activo = models.BooleanField(_('Activo'), default=True)
    created_at = models.DateTimeField(_('Fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Última actualización'), auto_now=True)

    class Meta:
        verbose_name = _('Servicio')
        verbose_name_plural = _('Servicios')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre 