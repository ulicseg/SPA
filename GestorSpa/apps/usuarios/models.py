from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver


class Perfil(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('cliente', 'Cliente'),
        ('profesional', 'Profesional'),
        ('administrador', 'Administrador'),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(_('Teléfono'), max_length=20, blank=True)
    direccion = models.TextField(_('Dirección'), blank=True)
    foto = models.ImageField(_('Foto de perfil'), upload_to='perfiles/', blank=True, null=True)
    bio = models.TextField(_('Biografía'), blank=True)
    fecha_nacimiento = models.DateField(_('Fecha de nacimiento'), null=True, blank=True)
    tipo_usuario = models.CharField(
        _('Tipo de usuario'), 
        max_length=20, 
        choices=TIPO_USUARIO_CHOICES, 
        default='cliente',
        help_text='Determina los permisos y accesos del usuario'
    )
    numero_licencia = models.CharField(
        _('Número de licencia profesional'), 
        max_length=50, 
        blank=True,
        help_text='Solo para profesionales'
    )
    especialidad = models.CharField(
        _('Especialidad'), 
        max_length=100, 
        blank=True,
        help_text='Especialidad del profesional'
    )
    activo = models.BooleanField(_('Activo'), default=True)
    created_at = models.DateTimeField(_('Fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Última actualización'), auto_now=True)

    class Meta:
        verbose_name = _('Perfil')
        verbose_name_plural = _('Perfiles')
        permissions = [
            ('can_manage_all_appointments', 'Puede gestionar todos los turnos'),
            ('can_view_reports', 'Puede ver reportes'),
            ('can_manage_professionals', 'Puede gestionar profesionales'),
        ]

    def __str__(self):
        return f"Perfil de {self.usuario.username} ({self.get_tipo_usuario_display()})"
    
    def get_rol_display(self):
        """Retorna el nombre del rol del usuario"""
        from .permissions import RoleManager
        role = RoleManager.get_user_role(self.usuario)
        if role:
            return RoleManager.ROLES[role]['name']
        return 'Sin rol asignado'
    
    def is_cliente(self):
        """Verifica si el usuario es cliente"""
        from .permissions import RoleManager
        return RoleManager.user_has_role(self.usuario, 'cliente')
    
    def is_profesional(self):
        """Verifica si el usuario es profesional"""
        from .permissions import RoleManager
        return RoleManager.user_has_role(self.usuario, 'profesional')
    
    def is_administrador(self):
        """Verifica si el usuario es administrador"""
        from .permissions import RoleManager
        return RoleManager.user_has_role(self.usuario, 'administrador')


class Profesional(models.Model):
    """
    Modelo extendido para información específica de profesionales
    """
    DIAS_SEMANA = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]
    
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('vacaciones', 'En Vacaciones'),
        ('licencia', 'En Licencia'),
    ]
    
    usuario = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profesional',
        help_text='Usuario asociado al profesional'
    )
    nombre_completo = models.CharField(
        _('Nombre completo'), 
        max_length=150,
        help_text='Nombre completo del profesional'
    )
    especialidad = models.CharField(
        _('Especialidad principal'), 
        max_length=100,
        help_text='Especialidad principal del profesional'
    )
    especialidades_secundarias = models.TextField(
        _('Especialidades secundarias'), 
        blank=True,
        help_text='Otras especialidades separadas por comas'
    )
    contacto = models.EmailField(
        _('Email de contacto'),
        help_text='Email profesional de contacto'
    )
    telefono_profesional = models.CharField(
        _('Teléfono profesional'), 
        max_length=20,
        blank=True
    )
    numero_matricula = models.CharField(
        _('Número de matrícula'), 
        max_length=50,
        unique=True,
        help_text='Número de matrícula profesional'
    )
    colegio_profesional = models.CharField(
        _('Colegio profesional'), 
        max_length=100,
        blank=True,
        help_text='Colegio o asociación profesional'
    )
    
    # Horarios de disponibilidad
    hora_inicio_lunes = models.TimeField(_('Lunes - Inicio'), null=True, blank=True)
    hora_fin_lunes = models.TimeField(_('Lunes - Fin'), null=True, blank=True)
    hora_inicio_martes = models.TimeField(_('Martes - Inicio'), null=True, blank=True)
    hora_fin_martes = models.TimeField(_('Martes - Fin'), null=True, blank=True)
    hora_inicio_miercoles = models.TimeField(_('Miércoles - Inicio'), null=True, blank=True)
    hora_fin_miercoles = models.TimeField(_('Miércoles - Fin'), null=True, blank=True)
    hora_inicio_jueves = models.TimeField(_('Jueves - Inicio'), null=True, blank=True)
    hora_fin_jueves = models.TimeField(_('Jueves - Fin'), null=True, blank=True)
    hora_inicio_viernes = models.TimeField(_('Viernes - Inicio'), null=True, blank=True)
    hora_fin_viernes = models.TimeField(_('Viernes - Fin'), null=True, blank=True)
    hora_inicio_sabado = models.TimeField(_('Sábado - Inicio'), null=True, blank=True)
    hora_fin_sabado = models.TimeField(_('Sábado - Fin'), null=True, blank=True)
    hora_inicio_domingo = models.TimeField(_('Domingo - Inicio'), null=True, blank=True)
    hora_fin_domingo = models.TimeField(_('Domingo - Fin'), null=True, blank=True)
    
    disponibilidad_notas = models.TextField(
        _('Notas sobre disponibilidad'), 
        blank=True,
        help_text='Información adicional sobre horarios y disponibilidad'
    )
    
    # Información adicional
    biografia = models.TextField(
        _('Biografía profesional'), 
        blank=True,
        help_text='Información sobre experiencia y formación'
    )
    experiencia_anos = models.PositiveIntegerField(
        _('Años de experiencia'), 
        default=0,
        help_text='Años de experiencia profesional'
    )
    foto_profesional = models.ImageField(
        _('Foto profesional'), 
        upload_to='profesionales/',
        blank=True, 
        null=True,
        help_text='Foto para mostrar en el perfil profesional'
    )
    servicios_especialidad = models.ManyToManyField(
        'servicios.Servicio',
        blank=True,
        verbose_name=_('Servicios de especialidad'),
        help_text='Servicios en los que se especializa este profesional'
    )
    
    # Estado y gestión
    estado = models.CharField(
        _('Estado'), 
        max_length=20, 
        choices=ESTADOS, 
        default='activo'
    )
    fecha_inicio = models.DateField(
        _('Fecha de inicio'), 
        help_text='Fecha de inicio en el spa'
    )
    fecha_fin = models.DateField(
        _('Fecha de fin'), 
        null=True, 
        blank=True,
        help_text='Fecha de finalización (si aplica)'
    )
    observaciones = models.TextField(
        _('Observaciones'), 
        blank=True,
        help_text='Observaciones internas sobre el profesional'
    )
    
    created_at = models.DateTimeField(_('Fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Última actualización'), auto_now=True)

    class Meta:
        verbose_name = _('Profesional')
        verbose_name_plural = _('Profesionales')
        ordering = ['nombre_completo']
        permissions = [
            ('can_view_professional_schedule', 'Puede ver horarios de profesionales'),
            ('can_manage_professional_data', 'Puede gestionar datos de profesionales'),
        ]

    def __str__(self):
        return f"{self.nombre_completo} - {self.especialidad}"
    
    def get_nombre_display(self):
        """Retorna el nombre para mostrar"""
        return self.nombre_completo or f"{self.usuario.first_name} {self.usuario.last_name}".strip()
    
    def get_horario_dia(self, dia_semana):
        """Obtiene el horario para un día específico"""
        inicio_attr = f"hora_inicio_{dia_semana.lower()}"
        fin_attr = f"hora_fin_{dia_semana.lower()}"
        
        inicio = getattr(self, inicio_attr, None)
        fin = getattr(self, fin_attr, None)
        
        if inicio and fin:
            return f"{inicio.strftime('%H:%M')} - {fin.strftime('%H:%M')}"
        return "No disponible"
    
    def get_horarios_semana(self):
        """Retorna un diccionario con los horarios de toda la semana"""
        horarios = {}
        dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        
        for dia in dias:
            horarios[dia] = self.get_horario_dia(dia)
        
        return horarios
    
    def esta_disponible_dia(self, dia_semana):
        """Verifica si está disponible un día específico"""
        inicio_attr = f"hora_inicio_{dia_semana.lower()}"
        fin_attr = f"hora_fin_{dia_semana.lower()}"
        
        inicio = getattr(self, inicio_attr, None)
        fin = getattr(self, fin_attr, None)
        
        return inicio is not None and fin is not None and self.estado == 'activo'
    
    def get_especialidades_todas(self):
        """Retorna todas las especialidades como lista"""
        especialidades = [self.especialidad]
        
        if self.especialidades_secundarias:
            secundarias = [esp.strip() for esp in self.especialidades_secundarias.split(',') if esp.strip()]
            especialidades.extend(secundarias)
        
        return especialidades


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea automáticamente un perfil cuando se crea un usuario"""
    if created:
        Perfil.objects.create(usuario=instance)


@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    """Guarda el perfil cuando se guarda el usuario"""
    if hasattr(instance, 'perfil'):
        instance.perfil.save()
