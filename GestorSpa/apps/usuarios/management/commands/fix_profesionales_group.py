from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from GestorSpa.apps.usuarios.models import Perfil

class Command(BaseCommand):
    help = 'Asegura que todos los usuarios con perfil profesional estén en el grupo Profesional.'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name='Profesional')
        self.stdout.write(self.style.SUCCESS(f"Grupo 'Profesional' {'creado' if created else 'ya existe'}."))

        profesionales = Perfil.objects.filter(tipo_usuario='profesional')
        self.stdout.write(f"Se encontraron {profesionales.count()} perfiles profesionales.")

        for perfil in profesionales:
            user = perfil.usuario
            if not user.groups.filter(name='Profesional').exists():
                user.groups.add(group)
                self.stdout.write(self.style.SUCCESS(f"Usuario {user.username} agregado al grupo Profesional."))
            else:
                self.stdout.write(f"Usuario {user.username} ya está en el grupo Profesional.")
