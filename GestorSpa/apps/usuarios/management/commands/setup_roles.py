from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from GestorSpa.apps.usuarios.permissions import RoleManager


class Command(BaseCommand):
    help = 'Configura los roles y permisos del sistema GestorSpa'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-groups',
            action='store_true',
            help='Crear grupos y asignar permisos',
        )
        parser.add_argument(
            '--assign-role',
            type=str,
            help='Asignar rol a usuario (formato: username:role)',
        )
        parser.add_argument(
            '--list-roles',
            action='store_true',
            help='Listar roles disponibles',
        )
        parser.add_argument(
            '--show-user-roles',
            action='store_true',
            help='Mostrar roles de todos los usuarios',
        )

    def handle(self, *args, **options):
        if options['create_groups']:
            self.stdout.write(
                self.style.SUCCESS('Creando grupos y configurando permisos...')
            )
            RoleManager.create_groups_and_permissions()
            self.stdout.write(
                self.style.SUCCESS('¡Grupos y permisos configurados exitosamente!')
            )

        if options['list_roles']:
            self.stdout.write(self.style.SUCCESS('\nRoles disponibles:'))
            for role_key, role_data in RoleManager.ROLES.items():
                self.stdout.write(f"  • {role_key}: {role_data['name']}")
                self.stdout.write(f"    {role_data['description']}")

        if options['assign_role']:
            try:
                username, role = options['assign_role'].split(':')
                user = User.objects.get(username=username)
                RoleManager.assign_role_to_user(user, role)
                self.stdout.write(
                    self.style.SUCCESS(f'Rol "{role}" asignado a "{username}"')
                )
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Formato incorrecto. Use: username:role')
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Usuario "{username}" no encontrado')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error: {str(e)}')
                )

        if options['show_user_roles']:
            self.stdout.write(self.style.SUCCESS('\nRoles de usuarios:'))
            for user in User.objects.all():
                role = RoleManager.get_user_role(user)
                role_display = role if role else 'Sin rol'
                self.stdout.write(f"  • {user.username}: {role_display}")

        if not any([options['create_groups'], options['assign_role'], 
                   options['list_roles'], options['show_user_roles']]):
            self.stdout.write(self.style.WARNING('Use --help para ver las opciones disponibles'))
