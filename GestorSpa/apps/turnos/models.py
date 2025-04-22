from django.db import models
from django.utils.translation import gettext_lazy as _
from GestorSpa.apps.servicios.models import Servicio

class Turno(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', _('Pendiente')),
        ('confirmado', _('Confirmado')),
        ('cancelado', _('Cancelado')),
        ('completado', _('Completado')),
    ]

    nombre = models.CharField(_('Nombre'), max_length=100)
    email = models.EmailField(_('Email'))
    telefono = models.CharField(_('Teléfono'), max_length=20)
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE, related_name='turnos')
    fecha = models.DateField(_('Fecha'))
    hora_inicio = models.TimeField(_('Hora de inicio'))
    hora_fin = models.TimeField(_('Hora de fin'))
    estado = models.CharField(_('Estado'), max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    notas = models.TextField(_('Notas'), null=True, blank=True)
    created_at = models.DateTimeField(_('Fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Última actualización'), auto_now=True)

    class Meta:
        verbose_name = _('Turno')
        verbose_name_plural = _('Turnos')
        ordering = ['-fecha', '-hora_inicio']
        unique_together = ['fecha', 'hora_inicio', 'servicio']

    def __str__(self):
        return f"{self.nombre} - {self.servicio} - {self.fecha} {self.hora_inicio}" 