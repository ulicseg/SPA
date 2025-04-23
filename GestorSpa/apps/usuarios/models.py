from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
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
        return f"Perfil de {self.usuario.username}"
