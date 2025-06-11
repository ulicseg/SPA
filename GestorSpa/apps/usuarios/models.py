from django.db import models
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model):
    ROLES_CHOICES = [
        ('cliente', _('Cliente')),
        ('profesional', _('Profesional')),
        ('administrador', _('Administrador')),
    ]
    
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(_('Rol'), max_length=20, choices=ROLES_CHOICES, default='cliente')
    telefono = models.CharField(_('Teléfono'), max_length=20, blank=True)
    direccion = models.TextField(_('Dirección'), blank=True)
    foto = models.ImageField(_('Foto de perfil'), upload_to='perfiles/', blank=True, null=True)
    bio = models.TextField(_('Biografía'), blank=True)
    fecha_nacimiento = models.DateField(_('Fecha de nacimiento'), null=True, blank=True)
    created_at = models.DateTimeField(_('Fecha de creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Última actualización'), auto_now=True)

    class Meta:
        verbose_name = _('Perfil')
        verbose_name_plural = _('Perfiles')

    def __str__(self):
        return f"Perfil de {self.usuario.username} - {self.get_rol_display()}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.asignar_grupo_por_rol()
    
    def asignar_grupo_por_rol(self):
        """Asigna el grupo correspondiente al usuario según su rol"""
        # Remover usuario de todos los grupos de roles
        grupos_roles = ['Clientes', 'Profesionales', 'Administradores']
        for grupo_name in grupos_roles:
            try:
                grupo = Group.objects.get(name=grupo_name)
                self.usuario.groups.remove(grupo)
            except Group.DoesNotExist:
                pass
        
        # Asignar al grupo correspondiente
        grupo_map = {
            'cliente': 'Clientes',
            'profesional': 'Profesionales', 
            'administrador': 'Administradores'
        }
        
        grupo_name = grupo_map.get(self.rol)
        if grupo_name:
            grupo, created = Group.objects.get_or_create(name=grupo_name)
            self.usuario.groups.add(grupo)


class Profesional(models.Model):
    ESPECIALIDADES_CHOICES = [
        ('masajes', _('Masajes Terapéuticos')),
        ('faciales', _('Tratamientos Faciales')),
        ('corporales', _('Tratamientos Corporales')),
        ('aromaterapia', _('Aromaterapia')),
        ('reflexologia', _('Reflexología')),
        ('hidroterapia', _('Hidroterapia')),
        ('spa', _('Servicios de Spa General')),
        ('bienestar', _('Bienestar Integral')),
        ('estetica', _('Estética Avanzada')),
        ('relajacion', _('Técnicas de Relajación')),
    ]
    
    DIAS_SEMANA = [
        ('lunes', _('Lunes')),
        ('martes', _('Martes')),
        ('miercoles', _('Miércoles')),
        ('jueves', _('Jueves')),
        ('viernes', _('Viernes')),
        ('sabado', _('Sábado')),
        ('domingo', _('Domingo')),
    ]
    
    # Relación con el usuario
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profesional')
    
    # Información profesional
    nombre_completo = models.CharField(_('Nombre Completo'), max_length=150)
    especialidad = models.CharField(_('Especialidad Principal'), max_length=50, choices=ESPECIALIDADES_CHOICES)
    especialidades_secundarias = models.ManyToManyField(
        'self', 
        through='EspecialidadSecundaria',
        symmetrical=False,
        blank=True,
        related_name='profesionales_secundarios',
        verbose_name=_('Especialidades Secundarias')
    )
    
    # Información de contacto
    telefono = models.CharField(_('Teléfono'), max_length=20)
    email_profesional = models.EmailField(_('Email Profesional'), blank=True)
    
    # Información profesional adicional
    numero_licencia = models.CharField(_('Número de Licencia'), max_length=50, blank=True)
    años_experiencia = models.PositiveIntegerField(_('Años de Experiencia'), default=0)
    certificaciones = models.TextField(_('Certificaciones'), blank=True, help_text="Lista de certificaciones y cursos")
    
    # Disponibilidad
    hora_inicio_disponibilidad = models.TimeField(_('Hora de Inicio'), default='09:00')
    hora_fin_disponibilidad = models.TimeField(_('Hora de Fin'), default='18:00')
    dias_disponibles = models.CharField(
        _('Días Disponibles'), 
        max_length=100, 
        help_text="Días de la semana separados por comas (lunes,martes,miercoles...)",
        default="lunes,martes,miercoles,jueves,viernes"
    )
    
    # Información adicional
    biografia = models.TextField(_('Biografía Profesional'), blank=True)
    foto_profesional = models.ImageField(_('Foto Profesional'), upload_to='profesionales/', blank=True, null=True)
    activo = models.BooleanField(_('Activo'), default=True)
    
    # Configuración de servicios
    servicios_que_ofrece = models.ManyToManyField(
        'servicios.Servicio',
        blank=True,
        related_name='profesionales',
        verbose_name=_('Servicios que Ofrece')
    )
    
    # Fechas
    fecha_contratacion = models.DateField(_('Fecha de Contratación'), null=True, blank=True)
    created_at = models.DateTimeField(_('Fecha de Creación'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Última Actualización'), auto_now=True)

    class Meta:
        verbose_name = _('Profesional')
        verbose_name_plural = _('Profesionales')
        ordering = ['nombre_completo']

    def __str__(self):
        return f"{self.nombre_completo} - {self.get_especialidad_display()}"
    
    def get_dias_disponibles_list(self):
        """Retorna una lista de los días disponibles"""
        if self.dias_disponibles:
            return [dia.strip() for dia in self.dias_disponibles.split(',')]
        return []
    
    def get_horario_completo(self):
        """Retorna el horario completo de disponibilidad"""
        dias = self.get_dias_disponibles_list()
        dias_display = [dict(self.DIAS_SEMANA).get(dia, dia) for dia in dias]
        return f"{', '.join(dias_display)} de {self.hora_inicio_disponibilidad} a {self.hora_fin_disponibilidad}"
    
    def es_disponible_dia(self, dia_semana):
        """Verifica si el profesional está disponible un día específico"""
        return dia_semana.lower() in self.get_dias_disponibles_list()
    
    def get_servicios_principales(self):
        """Retorna los primeros 3 servicios principales"""
        return self.servicios_que_ofrece.filter(activo=True)[:3]


class EspecialidadSecundaria(models.Model):
    """Modelo intermedio para especialidades secundarias"""
    profesional_principal = models.ForeignKey(
        Profesional, 
        on_delete=models.CASCADE,
        related_name='especialidades_extras'
    )
    profesional_especialidad = models.ForeignKey(
        Profesional,
        on_delete=models.CASCADE,
        related_name='profesionales_con_esta_especialidad'
    )
    nivel_competencia = models.CharField(
        _('Nivel de Competencia'),
        max_length=20,
        choices=[
            ('basico', _('Básico')),
            ('intermedio', _('Intermedio')),
            ('avanzado', _('Avanzado')),
            ('experto', _('Experto')),
        ],
        default='intermedio'
    )
    
    class Meta:
        verbose_name = _('Especialidad Secundaria')
        verbose_name_plural = _('Especialidades Secundarias')
        unique_together = ['profesional_principal', 'profesional_especialidad']


@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """Crea un perfil automáticamente cuando se crea un usuario"""
    if created:
        perfil = Perfil.objects.create(usuario=instance)
        # Si el usuario tiene el rol de profesional, crear también el modelo Profesional
        if perfil.rol == 'profesional':
            Profesional.objects.get_or_create(
                usuario=instance,
                defaults={
                    'nombre_completo': f"{instance.first_name} {instance.last_name}".strip() or instance.username,
                    'telefono': '',
                    'especialidad': 'spa',  # Especialidad por defecto
                }
            )

@receiver(post_save, sender=Perfil)
def crear_profesional_si_necesario(sender, instance, **kwargs):
    """Crea el modelo Profesional cuando se asigna el rol de profesional"""
    if instance.rol == 'profesional' and not hasattr(instance.usuario, 'profesional'):
        Profesional.objects.get_or_create(
            usuario=instance.usuario,
            defaults={
                'nombre_completo': f"{instance.usuario.first_name} {instance.usuario.last_name}".strip() or instance.usuario.username,
                'telefono': instance.telefono or '',
                'especialidad': 'spa',  # Especialidad por defecto
            }
        )
