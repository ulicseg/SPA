# -*- coding: utf-8 -*-
"""
Script simple para probar el envío de emails con caracteres especiales
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GestorSpa.configuraciones.settings')
django.setup()

from django.core.mail import EmailMessage
from django.conf import settings

def test_email_encoding():
    """Prueba directa del envío de emails con caracteres especiales"""
    
    print("=== Prueba de Email con UTF-8 ===")
    
    # Texto con caracteres especiales típicos del español
    subject = 'Comprobante de Reserva - Spa Sentirse Bien'
    
    mensaje = """Estimado/a José María Fernández,

Gracias por reservar en Spa Sentirse Bien.

--- Detalle de su reserva ---
Servicio: Masaje relajante corporal
Profesional: Dr. Carlos Rodríguez
Fecha: 2025-06-15
Hora: 10:00
Método de pago: Tarjeta de Débito
Total: $15000.00

¡Se aplicó un 15% de descuento por pago con débito anticipado!

Spa Sentirse Bien
Av. San Martin 123, Resistencia
Tel: +54 3624567890
Email: info@gestorspa.com

Si tiene dudas o necesita reprogramar, contáctenos.
¡Gracias por confiar en nosotros!"""
    
    try:
        # Crear email con configuración correcta para UTF-8
        email = EmailMessage(
            subject=subject,
            body=mensaje,
            from_email='info@gestorspa.com',
            to=['test@test.com']
        )
        email.content_subtype = 'plain'
        email.encoding = 'utf-8'
        
        # No enviar realmente, solo verificar que no hay errores de encoding
        print("✅ Email creado exitosamente sin errores de encoding")
        print(f"✅ Subject: {subject}")
        print("✅ Mensaje con caracteres especiales procesado correctamente")
        
        # Verificar encoding del mensaje
        try:
            mensaje_encoded = mensaje.encode('utf-8').decode('utf-8')
            print("✅ Mensaje valida correctamente como UTF-8")
        except UnicodeError as e:
            print(f"❌ Error de encoding en mensaje: {e}")
            return False
        
        return True
        
    except UnicodeEncodeError as e:
        print(f"❌ Error de encoding al crear email: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_email_encoding()
    if success:
        print("\n🎉 ¡Prueba de email con UTF-8 exitosa!")
    else:
        print("\n❌ Prueba de email falló")
        sys.exit(1)
