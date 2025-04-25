from django.db import models
from django.utils.translation import gettext_lazy as _
from GestorSpa.apps.servicios.models import Servicio
from datetime import timedelta, datetime

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
    hora_fin = models.TimeField(_('Hora de fin'), null=True, blank=True)
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

    def save(self, *args, **kwargs):
        if not self.hora_fin and self.hora_inicio and self.servicio:
            # Calcular hora_fin basado en la duración del servicio
            hora_inicio_dt = datetime.combine(self.fecha, self.hora_inicio)
            hora_fin_dt = hora_inicio_dt + timedelta(minutes=self.servicio.duracion)
            self.hora_fin = hora_fin_dt.time()
        super().save(*args, **kwargs)

    @staticmethod
    def get_horarios_disponibles(fecha, servicio):
        # Obtener todos los horarios posibles para el servicio
        hora_inicio = datetime.strptime(servicio.hora_inicio.strftime('%H:%M'), '%H:%M').time()
        hora_fin = datetime.strptime(servicio.hora_fin.strftime('%H:%M'), '%H:%M').time()
        
        # Convertir a datetime para facilitar los cálculos
        fecha_hora_inicio = datetime.combine(fecha, hora_inicio)
        fecha_hora_fin = datetime.combine(fecha, hora_fin)
        
        # Obtener turnos existentes
        turnos_existentes = Turno.objects.filter(
            fecha=fecha,
            servicio=servicio,
            estado__in=['pendiente', 'confirmado']
        ).values_list('hora_inicio', flat=True)
        
        # Generar horarios disponibles
        horarios_disponibles = []
        hora_actual = fecha_hora_inicio
        
        while hora_actual < fecha_hora_fin:
            hora_str = hora_actual.strftime('%H:%M')
            if hora_actual.time() not in turnos_existentes:
                horarios_disponibles.append(hora_str)
            hora_actual += timedelta(minutes=servicio.intervalo)
        
        return horarios_disponibles 