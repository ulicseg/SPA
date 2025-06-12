from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from GestorSpa.apps.usuarios.permissions import RoleManager
from GestorSpa.apps.usuarios.models import Perfil


class Command(BaseCommand):
    help = 'Crea usuarios de demostración con diferentes roles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Elimina usuarios demo existentes antes de crear nuevos',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Eliminando usuarios demo existentes...')
            User.objects.filter(username__in=['cliente_demo', 'profesional_demo', 'admin_demo']).delete()

        # Crear usuario Cliente
        self.create_user_with_role(
            username='cliente_demo',
            email='cliente@demo.com',
            first_name='María',
            last_name='González',
            password='demo123',
            role='cliente',
            phone='+54 9 11 1234-5678',
            address='Av. Corrientes 1234, CABA'
        )

        # Crear usuario Profesional
        self.create_user_with_role(
            username='profesional_demo',
            email='profesional@demo.com',
            first_name='Dr. Carlos',
            last_name='Rodríguez',
            password='demo123',
            role='profesional',
            phone='+54 9 11 8765-4321',
            license='MP-12345',
            specialty='Masajes Terapéuticos'
        )

        # Crear usuario Administrador
        self.create_user_with_role(
            username='admin_demo',
            email='admin@demo.com',
            first_name='Dra. Ana',
            last_name='Felicidad',
            password='demo123',
            role='administrador',
            phone='+54 9 11 5555-0000',
            is_staff=True,
            is_superuser=True
        )

        self.stdout.write(
            self.style.SUCCESS('✅ Usuarios demo creados exitosamente!')
        )
        self.stdout.write('\n📋 Credenciales de acceso:')
        self.stdout.write('🧑‍💼 Cliente: cliente_demo / demo123')
        self.stdout.write('👨‍⚕️ Profesional: profesional_demo / demo123')
        self.stdout.write('👩‍💼 Administrador: admin_demo / demo123')
        self.stdout.write('\n🔗 Inicia sesión en: http://127.0.0.1:8000/login/')

    def create_user_with_role(self, username, email, first_name, last_name, 
                             password, role, phone='', address='', license='', 
                             specialty='', is_staff=False, is_superuser=False):
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            self.stdout.write(f'⚠️  Usuario {username} ya existe, saltando...')
            return

        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser
        )

        # Obtener o crear perfil
        perfil, created = Perfil.objects.get_or_create(usuario=user)
        
        # Configurar perfil
        perfil.telefono = phone
        perfil.direccion = address
        perfil.tipo_usuario = role
        
        if role == 'profesional':
            perfil.numero_licencia = license
            perfil.especialidad = specialty
        
        perfil.save()

        # Asignar rol
        try:
            RoleManager.assign_role_to_user(user, role)
            role_name = RoleManager.ROLES[role]['name']
            self.stdout.write(
                self.style.SUCCESS(f'✅ Usuario {username} creado con rol: {role_name}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error asignando rol a {username}: {str(e)}')
            )
