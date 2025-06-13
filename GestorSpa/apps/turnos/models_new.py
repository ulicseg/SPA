# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _
from GestorSpa.apps.servicios.models import Servicio
from GestorSpa.apps.usuarios.models import Profesional
from datetime import timedelta, datetime
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


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
    profesional = models.ForeignKey(Profesional, on_delete=models.CASCADE, related_name='turnos', verbose_name=_('Profesional'))
    fecha = models.DateField(_('Fecha'))
    hora_inicio = models.TimeField(_('Hora de inicio'))
    hora_fin = models.TimeField(_('Hora de fin'), null=True, blank=True)
    estado = models.CharField(_('Estado'), max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    notas = models.TextField(_('Notas'), null=True, blank=True)
    created_at = models.DateTimeField(_('Fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Última actualización'), auto_now=True)
    metodo_pago = models.CharField(
        _('Método de pago'),
        max_length=20,
        choices=[('efectivo', 'Efectivo'), ('debito', 'Tarjeta de Débito'), ('credito', 'Tarjeta de Crédito')],
        default='efectivo'
    )
    pagado = models.BooleanField(_('Pagado'), default=False)
    descuento_aplicado = models.BooleanField(_('Descuento aplicado'), default=False)
    total = models.DecimalField(_('Total a pagar'), max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = _('Turno')
        verbose_name_plural = _('Turnos')
        ordering = ['-fecha', '-hora_inicio']
        unique_together = ['fecha', 'hora_inicio', 'servicio']

    def __str__(self):
        return f"{self.nombre} - {self.servicio} - {self.fecha} {self.hora_inicio}"

    def calcular_total(self):
        """Calcula el total considerando descuento por débito anticipado"""
        from decimal import Decimal
        base = self.servicio.precio
        descuento = Decimal('0')
        
        if self.metodo_pago == 'debito' and self.fecha >= timezone.now().date() + timedelta(days=2):
            descuento = base * Decimal('0.15')
            self.descuento_aplicado = True
        
        self.total = base - descuento
        return self.total

    def save(self, *args, **kwargs):
        self.calcular_total()
        super().save(*args, **kwargs)
        # Enviar comprobante si está pagado
        if self.pagado:
            self.enviar_comprobante()

    def enviar_comprobante(self):
        """Envía comprobante por email con manejo robusto de UTF-8"""
        try:
            from django.core.mail import EmailMessage
            from django.conf import settings
            import logging
            
            logger = logging.getLogger(__name__)
            
            # Asegurar que todos los strings sean UTF-8
            subject = 'Comprobante de Reserva - Spa Sentirse Bien'
            
            empresa = """Spa Sentirse Bien
Av. San Martin 123, Resistencia
Tel: +54 3624567890
Email: info@gestorspa.com"""
            
            # Construir mensaje parte por parte
            mensaje_lines = [
                f"Estimado/a {self.nombre},",
                "",
                "Gracias por reservar en Spa Sentirse Bien.",
                "",
                "--- Detalle de su reserva ---",
                f"Servicio: {self.servicio.nombre}",
                f"Profesional: {self.profesional}",
                f"Fecha: {self.fecha}",
                f"Hora: {self.hora_inicio}",
                f"Método de pago: {self.get_metodo_pago_display()}",
                f"Total: ${self.total:.2f}"
            ]
            
            if self.descuento_aplicado:
                mensaje_lines.append("¡Se aplicó un 15% de descuento por pago con débito anticipado!")
            
            mensaje_lines.extend([
                "",
                empresa,
                "",
                "Si tiene dudas o necesita reprogramar, contáctenos.",
                "¡Gracias por confiar en nosotros!"
            ])
            
            mensaje = '\n'.join(mensaje_lines)
            
            # Crear email con configuración explícita UTF-8
            email = EmailMessage(
                subject=subject,
                body=mensaje,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@gestorspa.com'),
                to=[self.email],
                charset='utf-8'
            )
            email.content_subtype = 'plain'
            email.encoding = 'utf-8'
            
            # Enviar email
            result = email.send(fail_silently=False)
            logger.info(f"Comprobante enviado exitosamente a {self.email}. Resultado: {result}")
            
        except UnicodeEncodeError as e:
            logger.error(f"Error de encoding al enviar comprobante: {str(e)}")
        except Exception as e:
            logger.error(f"Error general al enviar comprobante: {str(e)}")

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validar que el profesional puede realizar el servicio
        if self.profesional not in self.servicio.profesional_set.all():
            raise ValidationError('El profesional seleccionado no está habilitado para este servicio.')
            
        # Validar disponibilidad horaria
        dia = self.fecha.strftime('%A').lower()
        hora_inicio = self.hora_inicio
        hora_fin = (datetime.combine(self.fecha, self.hora_inicio) + timedelta(minutes=self.servicio.duracion)).time()
        
        # Obtener horario del profesional para ese día
        inicio_prof = getattr(self.profesional, f"hora_inicio_{dia}", None)
        fin_prof = getattr(self.profesional, f"hora_fin_{dia}", None)
        
        if not inicio_prof or not fin_prof:
            raise ValidationError('El profesional no tiene horario configurado para ese día.')
        
        if hora_inicio is None or hora_fin is None:
            raise ValidationError('El horario de inicio o fin del turno no está definido.')
        
        if not (inicio_prof <= hora_inicio and hora_fin <= fin_prof):
            raise ValidationError('El turno está fuera del horario disponible del profesional.')
        
        # Validar superposición de turnos
        solapados = Turno.objects.filter(
            profesional=self.profesional,
            fecha=self.fecha,
            estado__in=['pendiente', 'confirmado']
        ).exclude(pk=self.pk)
        
        for t in solapados:
            if t.hora_inicio is None or t.hora_fin is None:
                continue
            if (t.hora_inicio < hora_fin and hora_inicio < t.hora_fin):
                raise ValidationError('El profesional ya tiene un turno asignado en ese horario.')
        
        # Restricción de 48 horas
        if self.fecha < timezone.now().date() + timedelta(hours=48/24):
            raise ValidationError('Las reservas deben realizarse con al menos 48 horas de anticipación.')
        
        return super().clean()

    @staticmethod
    def get_horarios_disponibles(fecha, servicio):
        """Obtiene los horarios disponibles para un servicio en una fecha"""
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
