from django.contrib import admin
from .models import Turno

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'servicio', 'fecha', 'hora_inicio', 'estado')
    list_filter = ('estado', 'fecha', 'servicio')
    search_fields = ('nombre', 'email', 'telefono', 'notas')
    ordering = ('-fecha', '-hora_inicio')
    date_hierarchy = 'fecha' 