# -*- coding: utf-8 -*-
"""
Middleware para forzar encoding UTF-8 en todas las requests
"""
import logging

logger = logging.getLogger(__name__)


class UTF8EncodingMiddleware:
    """
    Middleware que asegura que todas las requests usen encoding UTF-8
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Forzar encoding UTF-8 en la request
        try:
            if hasattr(request, 'encoding'):
                request.encoding = 'utf-8'
            
            # Asegurar que los datos POST sean UTF-8
            if hasattr(request, 'POST') and request.POST:
                for key, value in request.POST.items():
                    if isinstance(value, str):
                        try:
                            # Verificar que el string es válido UTF-8
                            value.encode('utf-8').decode('utf-8')
                        except (UnicodeEncodeError, UnicodeDecodeError) as e:
                            logger.warning(f"Error de encoding en campo {key}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error en UTF8EncodingMiddleware: {str(e)}")
        
        response = self.get_response(request)
        
        # Asegurar que la response tenga charset UTF-8
        try:
            if hasattr(response, 'charset'):
                response.charset = 'utf-8'
            
            if hasattr(response, 'content_type') and 'charset' not in response.get('Content-Type', ''):
                response['Content-Type'] = f"{response.get('Content-Type', 'text/html')}; charset=utf-8"
                
        except Exception as e:
            logger.error(f"Error configurando charset en response: {str(e)}")
        
        return response
