from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
import time

User = get_user_model()

class Command(BaseCommand):
    help = 'Diagnóstico completo del sistema de password reset'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email para diagnóstico')
        parser.add_argument('--clear-cache', action='store_true', help='Limpiar cache')
        parser.add_argument('--test-email', action='store_true', help='Probar envío de email')

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("🔍 DIAGNÓSTICO DEL SISTEMA DE PASSWORD RESET")
        self.stdout.write("=" * 60)
        
        # 1. Verificar configuración de email
        self.check_email_config()
        
        # 2. Limpiar cache si se solicita
        if options.get('clear_cache'):
            self.clear_password_reset_cache()
        
        # 3. Probar email si se solicita
        if options.get('test_email') and options.get('email'):
            self.test_email_sending(options['email'])
        
        # 4. Verificar usuarios si se proporciona email
        if options.get('email'):
            self.check_user_exists(options['email'])
        
        self.stdout.write("=" * 60)
        self.stdout.write("✅ Diagnóstico completado")

    def check_email_config(self):
        self.stdout.write("\n📧 CONFIGURACIÓN DE EMAIL:")
        self.stdout.write(f"   Host: {settings.EMAIL_HOST}")
        self.stdout.write(f"   Puerto: {settings.EMAIL_PORT}")
        self.stdout.write(f"   TLS: {settings.EMAIL_USE_TLS}")
        self.stdout.write(f"   Usuario: {settings.EMAIL_HOST_USER}")
        self.stdout.write(f"   From: {settings.DEFAULT_FROM_EMAIL}")
        self.stdout.write(f"   Backend: {settings.EMAIL_BACKEND}")
        
        if hasattr(settings, 'EMAIL_TIMEOUT'):
            self.stdout.write(f"   Timeout: {settings.EMAIL_TIMEOUT}s")

    def clear_password_reset_cache(self):
        self.stdout.write("\n🧹 LIMPIANDO CACHE...")
        try:
            cache.clear()
            self.stdout.write(self.style.SUCCESS("   ✅ Cache limpiado exitosamente"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error limpiando cache: {e}"))

    def check_user_exists(self, email):
        self.stdout.write(f"\n👤 VERIFICANDO USUARIO: {email}")
        try:
            users = User.objects.filter(email__iexact=email)
            if users.exists():
                user = users.first()
                self.stdout.write(self.style.SUCCESS(f"   ✅ Usuario encontrado: {user.username}"))
                self.stdout.write(f"   📧 Email: {user.email}")
                self.stdout.write(f"   🟢 Activo: {user.is_active}")
                self.stdout.write(f"   📅 Último login: {user.last_login}")
            else:
                self.stdout.write(self.style.WARNING(f"   ⚠️ No se encontró usuario con email: {email}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error verificando usuario: {e}"))

    def test_email_sending(self, email):
        self.stdout.write(f"\n📬 PROBANDO ENVÍO DE EMAIL A: {email}")
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            result = send_mail(
                subject=f'Prueba de Email - GestorSPA [{timestamp}]',
                message=f'Email de prueba enviado el {timestamp}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            if result:
                self.stdout.write(self.style.SUCCESS(f"   ✅ Email enviado exitosamente"))
            else:
                self.stdout.write(self.style.WARNING(f"   ⚠️ Email no enviado (sin errores)"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ Error enviando email: {e}"))
            
            # Detectar tipos específicos de error
            error_str = str(e).lower()
            if 'timeout' in error_str:
                self.stdout.write("   💡 Sugerencia: Problema de timeout - verifica conexión")
            elif 'authentication' in error_str:
                self.stdout.write("   💡 Sugerencia: Error de autenticación - verifica credenciales")
            elif 'rate' in error_str or 'limit' in error_str:
                self.stdout.write("   💡 Sugerencia: Rate limiting - espera unos minutos")
            elif 'refused' in error_str:
                self.stdout.write("   💡 Sugerencia: Conexión rechazada - verifica firewall")
