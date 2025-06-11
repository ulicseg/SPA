from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Perfil, Profesional, EspecialidadSecundaria


class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'
    fields = ('rol', 'telefono', 'direccion', 'foto', 'bio', 'fecha_nacimiento')


class ProfesionalInline(admin.StackedInline):
    model = Profesional
    can_delete = False
    verbose_name_plural = 'Información Profesional'
    fields = (
        'nombre_completo', 'especialidad', 'telefono', 'email_profesional',
        'numero_licencia', 'años_experiencia', 'certificaciones',
        'hora_inicio_disponibilidad', 'hora_fin_disponibilidad', 'dias_disponibles',
        'biografia', 'foto_profesional', 'activo'
    )
    
    def get_fields(self, request, obj=None):
        """Mostrar campos solo si el usuario tiene rol de profesional"""
        if obj and hasattr(obj, 'perfil') and obj.perfil.rol == 'profesional':
            return self.fields
        return ()

    def has_add_permission(self, request, obj=None):
        """Solo permitir agregar si el usuario tiene rol profesional"""
        if obj and hasattr(obj, 'perfil'):
            return obj.perfil.rol == 'profesional'
        return False


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline, ProfesionalInline)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_rol', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'perfil__rol')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    def get_rol(self, obj):
        if hasattr(obj, 'perfil'):
            return obj.perfil.get_rol_display()
        return 'Sin perfil'
    get_rol.short_description = 'Rol'
    get_rol.admin_order_field = 'perfil__rol'


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'rol', 'telefono', 'created_at')
    list_filter = ('rol', 'created_at')
    search_fields = ('usuario__username', 'usuario__email', 'telefono')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('usuario', 'rol')
        }),
        ('Información de Contacto', {
            'fields': ('telefono', 'direccion')
        }),
        ('Información Personal', {
            'fields': ('foto', 'bio', 'fecha_nacimiento')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = (
        'nombre_completo', 'especialidad', 'telefono', 
        'activo', 'años_experiencia', 'created_at'
    )
    list_filter = ('especialidad', 'activo', 'años_experiencia', 'created_at')
    search_fields = ('nombre_completo', 'telefono', 'email_profesional', 'numero_licencia')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('servicios_que_ofrece',)
    
    fieldsets = (
        ('Información Personal', {
            'fields': ('usuario', 'nombre_completo', 'foto_profesional')
        }),
        ('Información Profesional', {
            'fields': (
                'especialidad', 'numero_licencia', 'años_experiencia', 
                'certificaciones', 'biografia'
            )
        }),
        ('Información de Contacto', {
            'fields': ('telefono', 'email_profesional')
        }),
        ('Disponibilidad', {
            'fields': (
                'hora_inicio_disponibilidad', 'hora_fin_disponibilidad', 
                'dias_disponibles'
            ),
            'description': 'Configure los horarios y días de disponibilidad del profesional'
        }),
        ('Servicios', {
            'fields': ('servicios_que_ofrece',),
            'description': 'Seleccione los servicios que puede ofrecer este profesional'
        }),
        ('Estado y Fechas', {
            'fields': ('activo', 'fecha_contratacion', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        """Personalizar el formulario"""
        form = super().get_form(request, obj, **kwargs)
        
        # Ayuda para el campo días disponibles
        if 'dias_disponibles' in form.base_fields:
            form.base_fields['dias_disponibles'].help_text = (
                "Introduzca los días separados por comas: lunes,martes,miercoles,jueves,viernes,sabado,domingo"
            )
        
        return form
    
    def save_model(self, request, obj, form, change):
        """Asegurar que el usuario tenga rol de profesional"""
        super().save_model(request, obj, form, change)
        
        # Verificar y actualizar el rol del perfil
        if hasattr(obj.usuario, 'perfil'):
            if obj.usuario.perfil.rol != 'profesional':
                obj.usuario.perfil.rol = 'profesional'
                obj.usuario.perfil.save()


@admin.register(EspecialidadSecundaria)
class EspecialidadSecundariaAdmin(admin.ModelAdmin):
    list_display = ('profesional_principal', 'profesional_especialidad', 'nivel_competencia')
    list_filter = ('nivel_competencia',)
    search_fields = (
        'profesional_principal__nombre_completo',
        'profesional_especialidad__nombre_completo'
    )


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
