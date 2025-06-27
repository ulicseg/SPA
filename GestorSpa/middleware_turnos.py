# -*- coding: utf-8 -*-
"""
Middleware para procesar automáticamente los turnos que deberían estar completados.

Este middleware se ejecuta en cada request y verifica si hay turnos que deberían
estar marcados como completados basándose en su fecha y hora programada.

NOTA: Este middleware se ejecuta en cada request, por lo que es recomendable
también configurar un task programado (cron job) para un mejor rendimiento
en producción.
"""

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from GestorSpa.apps.turnos.models import Turno
import logging
from datetime import datetime, timedelta


class AutoCompleteTurnosMiddleware(MiddlewareMixin):
    """
    Middleware que marca automáticamente los turnos como completados
    cuando su hora programada ha pasado.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)
        # Controlar la frecuencia de ejecución para evitar sobrecarga
        self.last_check = None
        self.check_interval = timedelta(minutes=15)  # Verificar cada 15 minutos
        
    def __call__(self, request):
        # Verificar si es momento de ejecutar la comprobación
        now = timezone.now()
        
        if (self.last_check is None or 
            (now - self.last_check) >= self.check_interval):
            
            self.process_expired_turnos()
            self.last_check = now
        
        response = self.get_response(request)
        return response
    
    def process_expired_turnos(self):
        """Procesa los turnos que deberían estar completados"""
        try:
            # Usar el método de clase del modelo
            resultado = Turno.marcar_completados_automaticamente()
            
            if resultado['turnos_marcados'] > 0:
                self.logger.info(
                    f"Auto-completado middleware: {resultado['turnos_marcados']} turnos marcados como completados"
                )
            
            # Log de errores si los hay
            for error in resultado['errores']:
                self.logger.error(f"Auto-completado middleware error: {error}")
                
        except Exception as e:
            self.logger.error(f"Error en auto-completado middleware: {str(e)}")
    
    def process_request(self, request):
        """Método heredado del MiddlewareMixin - no se usa actualmente"""
        return None
