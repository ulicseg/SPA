from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.utils import timezone
import re

class Command(BaseCommand):
    help = 'Gestiona el cache de rate limiting para password reset'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Limpiar todo el cache de rate limiting')
        parser.add_argument('--email', type=str, help='Limpiar cache para un email específico')
        parser.add_argument('--list', action='store_true', help='Listar todos los intentos en cache')

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_all_cache()
        elif options['email']:
            self.clear_email_cache(options['email'])
        elif options['list']:
            self.list_cache_entries()
        else:
            self.stdout.write(self.style.ERROR('Usa --clear, --email <email>, o --list'))

    def clear_all_cache(self):
        """Limpiar todo el cache de rate limiting"""
        self.stdout.write("🧹 Limpiando todo el cache de rate limiting...")
        
        # Como usamos cache de memoria local, podemos limpiar las claves específicas
        # En producción con Redis/Memcached esto sería diferente
        try:
            cache.clear()
            self.stdout.write(self.style.SUCCESS('✅ Cache limpiado completamente'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error limpiando cache: {str(e)}'))

    def clear_email_cache(self, email):
        """Limpiar cache para un email específico"""
        self.stdout.write(f"🧹 Limpiando cache para email: {email}")
        
        cache_key = f"password_reset_attempt_{email}"
        try:
            cache.delete(cache_key)
            self.stdout.write(self.style.SUCCESS(f'✅ Cache limpiado para {email}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))

    def list_cache_entries(self):
        """Listar entradas de cache (funcionalidad limitada con cache local)"""
        self.stdout.write("📋 Listando entradas de cache...")
        self.stdout.write("ℹ️  Con cache local no se pueden listar todas las claves")
        self.stdout.write("ℹ️  Usa --clear para limpiar todo o --email para limpiar uno específico")
        
        # Mostrar estado general
        now = timezone.now()
        self.stdout.write(f"🕐 Hora actual: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        self.stdout.write("💡 Límites configurados:")
        self.stdout.write("   • 3 intentos por hora por email")
        self.stdout.write("   • 5 minutos entre intentos")
