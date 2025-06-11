from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from GestorSpa.apps.usuarios.models import Perfil


class Command(BaseCommand):
    help = 'Crea usuarios de ejemplo con diferentes roles'

    def handle(self, *args, **options):
        self.stdout.write('Creando usuarios de ejemplo...')

        # Crear Dra. Ana Felicidad (Administradora)
        if not User.objects.filter(username='ana_felicidad').exists():
            admin_user = User.objects.create_user(
                username='ana_felicidad',
                email='ana.felicidad@gestorspa.com',
                password='admin123',
                first_name='Ana',
                last_name='Felicidad'
            )
            
            perfil_admin = Perfil.objects.get(usuario=admin_user)
            perfil_admin.rol = 'administrador'
            perfil_admin.telefono = '555-0001'
            perfil_admin.bio = 'Directora y fundadora del spa'
            perfil_admin.save()
            
            self.stdout.write(
                self.style.SUCCESS('Usuario administrador "ana_felicidad" creado')
            )
        else:
            self.stdout.write('Usuario "ana_felicidad" ya existe')

        # Crear usuario profesional de ejemplo
        if not User.objects.filter(username='maria_profesional').exists():
            prof_user = User.objects.create_user(
                username='maria_profesional',
                email='maria@gestorspa.com',
                password='prof123',
                first_name='María',
                last_name='García'
            )
            
            perfil_prof = Perfil.objects.get(usuario=prof_user)
            perfil_prof.rol = 'profesional'
            perfil_prof.telefono = '555-0002'
            perfil_prof.bio = 'Especialista en masajes terapéuticos'
            perfil_prof.save()
            
            self.stdout.write(
                self.style.SUCCESS('Usuario profesional "maria_profesional" creado')
            )
        else:
            self.stdout.write('Usuario "maria_profesional" ya existe')

        # Crear usuario cliente de ejemplo
        if not User.objects.filter(username='juan_cliente').exists():
            client_user = User.objects.create_user(
                username='juan_cliente',
                email='juan@email.com',
                password='client123',
                first_name='Juan',
                last_name='Pérez'
            )
            
            perfil_client = Perfil.objects.get(usuario=client_user)
            perfil_client.rol = 'cliente'
            perfil_client.telefono = '555-0003'
            perfil_client.save()
            
            self.stdout.write(
                self.style.SUCCESS('Usuario cliente "juan_cliente" creado')
            )
        else:
            self.stdout.write('Usuario "juan_cliente" ya existe')

        self.stdout.write(
            self.style.SUCCESS('\nUsuarios de ejemplo creados exitosamente!')
        )
        self.stdout.write('Credenciales:')
        self.stdout.write('- Administrador: ana_felicidad / admin123')
        self.stdout.write('- Profesional: maria_profesional / prof123')
        self.stdout.write('- Cliente: juan_cliente / client123')
