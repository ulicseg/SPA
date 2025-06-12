from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import Perfil, Profesional
from .permissions import RoleManager


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ('telefono', 'direccion', 'foto', 'bio', 'fecha_nacimiento', 
              'tipo_usuario', 'numero_licencia', 'especialidad', 'activo')


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 
                   'get_tipo_usuario', 'get_rol_asignado', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'perfil__tipo_usuario')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_tipo_usuario(self, obj):
        if hasattr(obj, 'perfil'):
            return obj.perfil.get_tipo_usuario_display()
        return '-'
    get_tipo_usuario.short_description = 'Tipo Usuario'
    
    def get_rol_asignado(self, obj):
        role = RoleManager.get_user_role(obj)
        if role:
            color = {
                'cliente': '#28a745',
                'profesional': '#007bff', 
                'administrador': '#dc3545'
            }.get(role, '#6c757d')
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color,
                RoleManager.ROLES[role]['name']
            )
        return format_html('<span style="color: #6c757d;">Sin rol</span>')
    get_rol_asignado.short_description = 'Rol Asignado'
    
    actions = ['asignar_rol_cliente', 'asignar_rol_profesional', 'asignar_rol_administrador']
    
    def asignar_rol_cliente(self, request, queryset):
        count = 0
        for user in queryset:
            RoleManager.assign_role_to_user(user, 'cliente')
            count += 1
        self.message_user(request, f'{count} usuarios asignados como clientes.')
    asignar_rol_cliente.short_description = "Asignar rol: Cliente"
    
    def asignar_rol_profesional(self, request, queryset):
        count = 0
        for user in queryset:
            RoleManager.assign_role_to_user(user, 'profesional')
            count += 1
        self.message_user(request, f'{count} usuarios asignados como profesionales.')
    asignar_rol_profesional.short_description = "Asignar rol: Profesional"
    
    def asignar_rol_administrador(self, request, queryset):
        count = 0
        for user in queryset:
            RoleManager.assign_role_to_user(user, 'administrador')
            count += 1
        self.message_user(request, f'{count} usuarios asignados como administradores.')
    asignar_rol_administrador.short_description = "Asignar rol: Administrador"


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'get_nombre_completo', 'telefono', 'tipo_usuario', 
                   'get_rol_asignado', 'activo', 'created_at')
    list_filter = ('tipo_usuario', 'activo', 'created_at')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 
                    'telefono', 'especialidad')
    readonly_fields = ('created_at', 'updated_at', 'get_rol_asignado')
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('usuario', 'telefono', 'direccion', 'foto', 'bio', 'fecha_nacimiento')
        }),
        ('Información Profesional', {
            'fields': ('tipo_usuario', 'numero_licencia', 'especialidad'),
            'description': 'Solo completar para profesionales'
        }),
        ('Estado y Rol', {
            'fields': ('activo', 'get_rol_asignado'),
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_nombre_completo(self, obj):
        return f"{obj.usuario.first_name} {obj.usuario.last_name}".strip() or obj.usuario.username
    get_nombre_completo.short_description = 'Nombre Completo'
    
    def get_rol_asignado(self, obj):
        role = RoleManager.get_user_role(obj.usuario)
        if role:
            color = {
                'cliente': '#28a745',
                'profesional': '#007bff', 
                'administrador': '#dc3545'
            }.get(role, '#6c757d')
            return format_html(
                '<span style="color: {}; font-weight: bold;">{}</span>',
                color,
                RoleManager.ROLES[role]['name']
            )
        return format_html('<span style="color: #6c757d;">Sin rol</span>')
    get_rol_asignado.short_description = 'Rol Asignado'


@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'especialidad', 'numero_matricula', 
                   'estado', 'get_usuario_email', 'get_horarios_resumen')
    list_filter = ('estado', 'especialidad', 'fecha_inicio')
    search_fields = ('nombre_completo', 'numero_matricula', 'especialidad', 
                    'usuario__username', 'usuario__email', 'contacto')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('usuario', 'nombre_completo', 'contacto', 'telefono_profesional', 'foto_profesional')
        }),
        ('Información Profesional', {
            'fields': ('especialidad', 'especialidades_secundarias', 'numero_matricula', 
                      'colegio_profesional', 'experiencia_anos', 'biografia')
        }),
        ('Horarios - Lunes a Viernes', {
            'fields': (
                ('hora_inicio_lunes', 'hora_fin_lunes'),
                ('hora_inicio_martes', 'hora_fin_martes'),
                ('hora_inicio_miercoles', 'hora_fin_miercoles'),
                ('hora_inicio_jueves', 'hora_fin_jueves'),
                ('hora_inicio_viernes', 'hora_fin_viernes'),
            )
        }),
        ('Horarios - Fin de Semana', {
            'fields': (
                ('hora_inicio_sabado', 'hora_fin_sabado'),
                ('hora_inicio_domingo', 'hora_fin_domingo'),
            ),
            'classes': ('collapse',)
        }),
        ('Disponibilidad y Servicios', {
            'fields': ('disponibilidad_notas', 'servicios_especialidad')
        }),
        ('Estado y Gestión', {
            'fields': ('estado', 'fecha_inicio', 'fecha_fin', 'observaciones')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    filter_horizontal = ('servicios_especialidad',)
    
    def get_usuario_email(self, obj):
        return obj.usuario.email if obj.usuario else '-'
    get_usuario_email.short_description = 'Email Usuario'
    
    def get_horarios_resumen(self, obj):
        horarios = []
        dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes']
        for dia in dias:
            if obj.esta_disponible_dia(dia):
                horarios.append(dia.capitalize()[:3])
        
        if horarios:
            return f"Disponible: {', '.join(horarios)}"
        return "Sin horarios configurados"
    get_horarios_resumen.short_description = 'Horarios'
    
    def save_model(self, request, obj, form, change):
        # Asegurar que el usuario tenga rol de profesional
        super().save_model(request, obj, form, change)
        if obj.usuario:
            RoleManager.assign_role_to_user(obj.usuario, 'profesional')
            # Actualizar perfil con información profesional
            perfil, created = Perfil.objects.get_or_create(usuario=obj.usuario)
            perfil.tipo_usuario = 'profesional'
            perfil.numero_licencia = obj.numero_matricula
            perfil.especialidad = obj.especialidad
            perfil.save()


# Reemplazar el UserAdmin predeterminado
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
