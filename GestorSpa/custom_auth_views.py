# -*- coding: utf-8 -*-
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import time
import logging

User = get_user_model()

class CustomPasswordResetView(PasswordResetView):
    """Vista personalizada para password reset que maneja correctamente el request"""
    template_name = 'auth/password_reset.html'
    email_template_name = 'auth/password_reset_email.html'
    subject_template_name = 'auth/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    form_class = PasswordResetForm
    
    def check_rate_limit(self, email):
        """Verificar si se puede enviar email basado en rate limiting"""
        # Clave para el cache específica del email
        cache_key = f"password_reset_attempt_{email}"
        
        # Obtener intentos previos
        attempts = cache.get(cache_key, [])
        now = timezone.now()
        
        # Limpiar intentos antiguos (más de 1 hora)
        attempts = [attempt for attempt in attempts 
                   if now - attempt < timedelta(hours=1)]
        
        # Verificar límites
        if len(attempts) >= 3:  # Máximo 3 intentos por hora
            return False, f"Has superado el límite de intentos (3 por hora). Último intento hace {int((now - attempts[-1]).total_seconds() / 60)} minutos."
        
        # Verificar si el último intento fue hace menos de 5 minutos
        if attempts and now - attempts[-1] < timedelta(minutes=5):
            wait_time = 5 - int((now - attempts[-1]).total_seconds() / 60)
            return False, f"Debes esperar {wait_time} minutos antes de intentar nuevamente."
        
        # Registrar este intento
        attempts.append(now)
        cache.set(cache_key, attempts, 3600)  # 1 hora
        
        return True, None
    
    def form_valid(self, form):
        """Override para manejar el envío de email con mejor control"""
        logger = logging.getLogger(__name__)
        
        email = form.cleaned_data['email']
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"🔍 [{timestamp}] Password reset solicitado para: {email}")
        
        # Verificar rate limiting
        can_proceed, rate_limit_msg = self.check_rate_limit(email)
        if not can_proceed:
            logger.warning(f"⏰ [{timestamp}] Rate limit alcanzado para {email}: {rate_limit_msg}")
            messages.warning(self.request, f"⏰ {rate_limit_msg}")
            return render(self.request, self.template_name, {'form': form})
        
        try:
            # Verificar si el usuario existe antes de proceder
            users = User.objects.filter(email__iexact=email, is_active=True)
            if users.exists():
                logger.info(f"✅ [{timestamp}] Usuario encontrado para email: {email}")
                
                # Enviar email personalizado con HTML forzado
                from django.core.mail import EmailMultiAlternatives
                from django.template.loader import render_to_string
                
                user = users.first()
                
                # Generar token y uid
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                
                # Crear contexto
                context = {
                    'user': user,
                    'uid': uid,
                    'token': token,
                    'protocol': 'http' if settings.DEBUG else 'https',
                    'domain': self.request.get_host(),
                    'site_name': 'GestorSPA',
                }
                
                # Renderizar email HTML
                html_content = render_to_string('auth/password_reset_email.html', context)
                text_content = f"""
Hola {user.get_full_name() or user.username},

Recibimos una solicitud para restablecer tu contraseña en GestorSPA.

Haz clic en este enlace para restablecer tu contraseña:
{context['protocol']}://{context['domain']}/reset/{uid}/{token}/

Este enlace expira en 1 hora por seguridad.

Si no solicitaste este cambio, ignora este email.

Saludos,
Equipo GestorSPA
"""
                
                # Crear email con HTML
                msg = EmailMultiAlternatives(
                    subject='Recuperación de contraseña - GestorSPA',
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                
                logger.info(f"✅ [{timestamp}] Email HTML enviado correctamente para: {email}")
            else:
                logger.info(f"⚠️ [{timestamp}] No se encontró usuario activo para email: {email}")
            
            # Agregar mensaje de éxito personalizado
            messages.success(
                self.request, 
                f'✅ Solicitud procesada para {email}. Si el email existe en nuestro sistema, recibirás las instrucciones en unos minutos. Revisa también tu carpeta de spam.'
            )
            
            logger.info(f"✅ [{timestamp}] Password reset procesado exitosamente para: {email}")
            
            # Redirigir a la página de éxito
            from django.shortcuts import redirect
            return redirect(self.success_url)
            
        except Exception as e:
            logger.error(f"❌ [{timestamp}] Error en password reset para {email}: {str(e)}")
            import traceback
            logger.error(f"📋 [{timestamp}] Traceback completo: {traceback.format_exc()}")
            
            # Verificar diferentes tipos de errores
            error_msg = str(e).lower()
            
            if any(keyword in error_msg for keyword in ['timeout', 'timed out']):
                logger.warning(f"⏰ [{timestamp}] Timeout detectado para {email}")
                messages.warning(
                    self.request,
                    '⏰ El servidor de email está tardando en responder. El email puede llegar con retraso. Si no lo recibes en 10 minutos, inténtalo nuevamente.'
                )
            elif any(keyword in error_msg for keyword in ['rate', 'limit', 'throttl', 'quota', 'temporary']):
                logger.warning(f"🚫 [{timestamp}] Rate limiting/Quota detectado para {email}")
                messages.warning(
                    self.request,
                    '🚫 El servidor de email está temporalmente ocupado. Intenta nuevamente en 10-15 minutos.'
                )
            elif any(keyword in error_msg for keyword in ['authentication', 'auth', 'credential']):
                logger.error(f"🔐 [{timestamp}] Error de autenticación de email para {email}")
                if settings.DEBUG:
                    messages.error(
                        self.request,
                        f'🔐 Error de autenticación del servidor de email. Verifica las credenciales en .env'
                    )
                else:
                    messages.error(
                        self.request,
                        '🔐 Error de configuración del servidor. Contacta al administrador.'
                    )
            else:
                # Error genérico
                if settings.DEBUG:
                    messages.error(
                        self.request,
                        f'❌ Error técnico: {str(e)}. Verifica la configuración de email.'
                    )
                else:
                    messages.error(
                        self.request,
                        '❌ Error temporal. Por favor, inténtalo nuevamente en unos minutos.'
                    )
            
            # En caso de error, volver al formulario
            return render(self.request, self.template_name, {'form': form})
    
    def get_context_data(self, **kwargs):
        """Agregar contexto adicional al template"""
        context = super().get_context_data(**kwargs)
        context['site_name'] = 'GestorSPA'
        return context
