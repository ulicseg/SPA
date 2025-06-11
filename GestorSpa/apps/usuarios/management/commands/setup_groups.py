from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from GestorSpa.apps.servicios.models import Servicio
from GestorSpa.apps.turnos.models import Turno


class Command(BaseCommand):
    help = 'Configura los grupos de usuarios y sus permisos'

    def handle(self, *args, **options):
        self.stdout.write('Configurando grupos y permisos...')

        # Crear grupos
        grupo_clientes, created = Group.objects.get_or_create(name='Clientes')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo "Clientes" creado'))
        
        grupo_profesionales, created = Group.objects.get_or_create(name='Profesionales')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo "Profesionales" creado'))
        
        grupo_administradores, created = Group.objects.get_or_create(name='Administradores')
        if created:
            self.stdout.write(self.style.SUCCESS('Grupo "Administradores" creado'))

        # Obtener content types
        turno_ct = ContentType.objects.get_for_model(Turno)
        servicio_ct = ContentType.objects.get_for_model(Servicio)

        # Permisos para Clientes
        permisos_clientes = [
            Permission.objects.get(content_type=turno_ct, codename='add_turno'),
            Permission.objects.get(content_type=turno_ct, codename='view_turno'),
        ]
        
        for permiso in permisos_clientes:
            grupo_clientes.permissions.add(permiso)
        
        self.stdout.write('Permisos asignados al grupo "Clientes"')

        # Permisos para Profesionales
        permisos_profesionales = [
            Permission.objects.get(content_type=turno_ct, codename='view_turno'),
            Permission.objects.get(content_type=turno_ct, codename='change_turno'),
            Permission.objects.get(content_type=servicio_ct, codename='view_servicio'),
        ]
        
        for permiso in permisos_profesionales:
            grupo_profesionales.permissions.add(permiso)
        
        self.stdout.write('Permisos asignados al grupo "Profesionales"')

        # Permisos para Administradores (todos los permisos)
        permisos_administradores = [
            # Permisos de Turnos
            Permission.objects.get(content_type=turno_ct, codename='add_turno'),
            Permission.objects.get(content_type=turno_ct, codename='view_turno'),
            Permission.objects.get(content_type=turno_ct, codename='change_turno'),
            Permission.objects.get(content_type=turno_ct, codename='delete_turno'),
            # Permisos de Servicios
            Permission.objects.get(content_type=servicio_ct, codename='add_servicio'),
            Permission.objects.get(content_type=servicio_ct, codename='view_servicio'),
            Permission.objects.get(content_type=servicio_ct, codename='change_servicio'),
            Permission.objects.get(content_type=servicio_ct, codename='delete_servicio'),
        ]
        
        for permiso in permisos_administradores:
            grupo_administradores.permissions.add(permiso)
        
        self.stdout.write('Permisos asignados al grupo "Administradores"')

        self.stdout.write(
            self.style.SUCCESS('Configuración de grupos y permisos completada exitosamente')
        )
