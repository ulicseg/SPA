# -*- coding: utf-8 -*-
"""
Script de inicialización para configurar encoding UTF-8 en todo el sistema
"""
import sys
import os
import locale

def configurar_encoding():
    """Configura el encoding UTF-8 para todo el sistema"""
    
    # Configurar variables de entorno
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    os.environ['LC_ALL'] = 'es_ES.UTF-8'
    os.environ['LANG'] = 'es_ES.UTF-8'
    
    # Configurar el locale del sistema
    try:
        if sys.platform.startswith('win'):
            # Para Windows
            locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
        else:
            # Para sistemas Unix/Linux
            locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    except locale.Error:
        try:
            # Fallback para Windows
            locale.setlocale(locale.LC_ALL, 'Spanish_Spain.1252')
        except locale.Error:
            # Último recurso
            locale.setlocale(locale.LC_ALL, '')
    
    # Configurar stdio para UTF-8
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    # Configurar encoding por defecto en Python
    if hasattr(sys, 'setdefaultencoding'):
        sys.setdefaultencoding('utf-8')

# Ejecutar configuración al importar
configurar_encoding()
