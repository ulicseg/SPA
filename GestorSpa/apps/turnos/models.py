# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from GestorSpa.apps.servicios.models import Servicio
from GestorSpa.apps.usuarios.models import Profesional
from datetime import timedelta, datetime
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone


class Turno(models.Model):
    ESTADO_CHOICES = [        ('pendiente', _('Pendiente')),
        ('confirmado', _('Confirmado')),
        ('cancelado', _('Cancelado')),
        ('completado', _('Completado')),
    ]

    nombre = models.CharField(_('Nombre'), max_length=100)
    email = models.EmailField(_('Email'))
    telefono = models.CharField(_('Teléfono'), max_length=20)
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name=_('Usuario'), 
        help_text='Usuario registrado que realizó la reserva (obligatorio)'
    )
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
        # Calcular hora de fin si no está definida
        if not self.hora_fin:
            self.calcular_hora_fin()
        super().save(*args, **kwargs)
        # Enviar comprobante si está pagado
        if self.pagado:
            self.enviar_comprobante()

    def enviar_confirmacion_reserva(self):
        """Envía email de confirmación de reserva con diseño profesional"""
        try:
            from django.core.mail import EmailMultiAlternatives
            from django.template.loader import render_to_string
            from django.conf import settings
            from django.utils import timezone
            import logging
            
            logger = logging.getLogger(__name__)
            
            # Log inicial
            logger.info(f"Iniciando envío de confirmación para turno {self.id} a {self.email}")
            
            # Validar email
            if not self.email:
                logger.error(f"Email vacío para turno {self.id}")
                raise ValueError("Email no válido o vacío")
            
            # Contexto para el template
            context = {
                'turno': self,
                'current_year': timezone.now().year,
                'spa_name': 'Spa Sentirse Bien',
                'spa_address': 'Av. San Martín 123, Resistencia',
                'spa_phone': '+54 3624-567890',
                'spa_email': 'info@gestorspa.com',
                'spa_whatsapp': '+54 9 3624-567890'
            }
            
            logger.info(f"Contexto creado para template: {context.keys()}")
            
            # Renderizar template HTML
            try:
                html_content = render_to_string('emails/confirmacion_reserva.html', context)
                logger.info(f"Template HTML renderizado exitosamente. Longitud: {len(html_content)}")
            except Exception as e:
                logger.error(f"Error al renderizar template HTML: {str(e)}")
                raise
            
            # Formatear fecha y hora de manera segura
            if hasattr(self.fecha, 'strftime'):
                fecha_str = self.fecha.strftime('%A, %d de %B de %Y')
            else:
                fecha_str = str(self.fecha)
                
            if hasattr(self.hora_inicio, 'strftime'):
                hora_str = self.hora_inicio.strftime('%H:%M')
            else:
                hora_str = str(self.hora_inicio)

            # Crear versión texto plano
            text_content = f"""
¡Hola {self.nombre}!

Confirmamos tu reserva en Spa Sentirse Bien:

DETALLES DE TU RESERVA:
• Servicio: {self.servicio.nombre}
• Profesional: {self.profesional.nombre_completo}
• Fecha: {fecha_str}
• Hora: {hora_str}
• Duración: {self.servicio.duracion} minutos
• Total: ${self.total:.2f}

INFORMACIÓN IMPORTANTE:
• Llega 10 minutos antes de tu cita
• Trae ropa cómoda y suelta
• Si necesitas cancelar, hazlo con 24hs de anticipación
• El pago se realizará al finalizar el servicio

CONTACTO:
📍 Av. San Martín 123, Resistencia
📞 +54 3624-567890
✉️ info@gestorspa.com
💬 WhatsApp: +54 9 3624-567890

¡Esperamos verte pronto!

Spa Sentirse Bien
Tu momento de relajación y bienestar
            """.strip()
            
            # Configurar email
            subject = f'Confirmación de Reserva - {self.servicio.nombre} - Spa Sentirse Bien'
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@gestorspa.com')
            
            logger.info(f"Configurando email: subject='{subject}', from='{from_email}', to='{self.email}'")
            
            # Crear email multipart
            try:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=from_email,
                    to=[self.email]
                )
                logger.info("EmailMultiAlternatives creado exitosamente")
            except Exception as e:
                logger.error(f"Error al crear EmailMultiAlternatives: {str(e)}")
                raise
            
            # Adjuntar versión HTML
            try:
                email.attach_alternative(html_content, "text/html")
                logger.info("HTML adjuntado exitosamente")
            except Exception as e:
                logger.error(f"Error al adjuntar HTML: {str(e)}")
                raise
            
            # Enviar email
            try:
                result = email.send(fail_silently=False)
                logger.info(f"Email enviado exitosamente a {self.email}. Resultado: {result}")
                return True
            except Exception as e:
                logger.error(f"Error al enviar email: {str(e)}")
                raise
            
        except Exception as e:
            logger.error(f"Error al enviar email de confirmación: {str(e)}")
            raise e

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
                "¡Gracias por confiar en nosotros!"            ])
            
            mensaje = '\n'.join(mensaje_lines)
            
            # Crear email con configuración explícita UTF-8
            email = EmailMessage(
                subject=subject,
                body=mensaje,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'info@gestorspa.com'),
                to=[self.email]
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
        
        # Validar campos obligatorios
        if not self.hora_inicio:
            raise ValidationError('La hora de inicio es requerida.')
        
        # Validar que el profesional puede realizar el servicio
        if not self.profesional.servicios_especialidad.filter(id=self.servicio.id).exists():
            raise ValidationError('El profesional seleccionado no está habilitado para este servicio.')
            
        # Validar disponibilidad horaria        # Obtener día de la semana en inglés para evitar problemas de locale
        import locale
        try:
            # Guardar locale actual
            current_locale = locale.getlocale()
            # Cambiar temporalmente a inglés
            locale.setlocale(locale.LC_TIME, 'C')
            dia = self.fecha.strftime('%A').lower()
            # Restaurar locale
            locale.setlocale(locale.LC_TIME, current_locale)
        except:
            # Si no se puede cambiar el locale, usar el mapeo manual
            weekday = self.fecha.weekday()  # 0=Monday, 1=Tuesday, etc.
            dias_ingles = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            dia = dias_ingles[weekday]
        
        # Convertir días en inglés a español
        dias_conversion = {
            'monday': 'lunes',
            'tuesday': 'martes', 
            'wednesday': 'miercoles',
            'thursday': 'jueves',
            'friday': 'viernes',
            'saturday': 'sabado',
            'sunday': 'domingo'
        }
        dia_es = dias_conversion.get(dia, dia)
        
        hora_inicio = self.hora_inicio
        hora_fin = (datetime.combine(self.fecha, self.hora_inicio) + timedelta(minutes=self.servicio.duracion)).time()
        
        # Obtener horario del profesional para ese día
        inicio_prof = getattr(self.profesional, f"hora_inicio_{dia_es}", None)
        fin_prof = getattr(self.profesional, f"hora_fin_{dia_es}", None)
        
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

    def puede_cambiar_estado(self, nuevo_estado):
        """Valida si se puede cambiar al nuevo estado según la lógica de negocio"""
        transiciones_permitidas = {
            'pendiente': ['confirmado', 'cancelado'],
            'confirmado': ['completado', 'cancelado'],
            'completado': [],  # Los turnos completados no pueden cambiar
            'cancelado': []    # Los turnos cancelados no pueden cambiar
        }
        
        return nuevo_estado in transiciones_permitidas.get(self.estado, [])
    
    def cambiar_estado(self, nuevo_estado, usuario=None):
        """Cambia el estado del turno validando las transiciones permitidas"""
        if not self.puede_cambiar_estado(nuevo_estado):
            from django.core.exceptions import ValidationError
            raise ValidationError(
                f'No se puede cambiar el estado de "{self.get_estado_display()}" a "{dict(self.ESTADO_CHOICES)[nuevo_estado]}"'
            )
        
        estado_anterior = self.estado
        self.estado = nuevo_estado
        self.save()
        
        # Log del cambio de estado si se proporciona usuario
        if usuario:
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f'Turno {self.id}: Estado cambiado de "{estado_anterior}" a "{nuevo_estado}" por {usuario.username}')
        
        return True

    def puede_ser_completado(self):
        """Verifica si el turno puede ser marcado como completado"""
        return (
            self.estado == 'confirmado' and 
            self.fecha <= timezone.now().date()
        )

    def puede_ser_cancelado(self):
        """Verifica si el turno puede ser cancelado"""
        return self.estado in ['pendiente', 'confirmado']

    def calcular_hora_fin(self):
        """Calcula y establece la hora de fin basada en la duración del servicio"""
        if self.hora_inicio and self.servicio and self.servicio.duracion:
            # Combinar fecha y hora para hacer el cálculo
            datetime_inicio = datetime.combine(self.fecha, self.hora_inicio)
            datetime_fin = datetime_inicio + timedelta(minutes=self.servicio.duracion)
            self.hora_fin = datetime_fin.time()
        return self.hora_fin

    def get_hora_fin_calculada(self):
        """Obtiene la hora de fin, calculándola si no está definida"""
        if self.hora_fin:
            return self.hora_fin
        return self.calcular_hora_fin()

    def ha_pasado_hora_fin(self):
        """Verifica si la hora de fin del turno ya pasó"""
        hora_fin = self.get_hora_fin_calculada()
        if not hora_fin:
            return False
        
        now = timezone.now()
        # Si es un día anterior, definitivamente ya pasó
        if self.fecha < now.date():
            return True
        # Si es el día actual, verificar la hora
        elif self.fecha == now.date():
            return hora_fin <= now.time()
        # Si es un día futuro, no ha pasado
        else:
            return False

    def deberia_estar_completado(self):
        """Verifica si el turno debería estar marcado como completado automáticamente"""
        return (
            self.estado == 'confirmado' and 
            self.ha_pasado_hora_fin()
        )

    @classmethod
    def marcar_completados_automaticamente(cls):
        """Método de clase para marcar automáticamente turnos como completados"""
        turnos_a_completar = cls.objects.filter(estado='confirmado')
        turnos_marcados = 0
        errores = []
        
        for turno in turnos_a_completar:
            if turno.deberia_estar_completado():
                try:
                    turno.cambiar_estado('completado')
                    turnos_marcados += 1
                except Exception as e:
                    errores.append(f"Turno {turno.id}: {str(e)}")
        
        return {
            'turnos_marcados': turnos_marcados,
            'errores': errores
        }
