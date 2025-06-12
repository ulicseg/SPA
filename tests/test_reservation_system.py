# -*- coding: utf-8 -*-
"""
Script de prueba completo del sistema de reservas con encoding UTF-8
"""
import os
import sys
import django
from datetime import date, time, timedelta

# Configurar Django
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GestorSpa.configuraciones.settings')
django.setup()

from django.contrib.auth.models import User
from GestorSpa.apps.turnos.models import Turno
from GestorSpa.apps.servicios.models import Servicio
from GestorSpa.apps.usuarios.models import Profesional

def test_system_with_existing_data():
    """Prueba el sistema usando datos existentes en la base de datos"""
    
    print("=== Prueba del Sistema con Datos Existentes ===")
    
    try:
        # Usar servicios y profesionales existentes
        servicio = Servicio.objects.first()
        profesional = Profesional.objects.first()
        
        if not servicio:
            print("❌ No hay servicios en la base de datos")
            return False
            
        if not profesional:
            print("❌ No hay profesionales en la base de datos")
            return False
        
        print(f"✅ Usando servicio: {servicio.nombre}")
        print(f"✅ Usando profesional: {profesional.nombre_completo}")
        
        # Datos de prueba con caracteres especiales
        test_data = {
            'nombre': 'José María Fernández Peña',
            'email': 'jose.maria@test.com',
            'telefono': '+54 3624 567890',
            'metodo_pago': 'debito'
        }
        
        # Crear turno de prueba
        fecha_prueba = date.today() + timedelta(days=3)
        hora_prueba = time(14, 0)  # 2 PM
        
        turno = Turno(
            nombre=test_data['nombre'],
            email=test_data['email'],
            telefono=test_data['telefono'],
            servicio=servicio,
            profesional=profesional,
            fecha=fecha_prueba,
            hora_inicio=hora_prueba,
            metodo_pago=test_data['metodo_pago']
        )
        
        print("📝 Datos del turno creados")
        
        # Calcular total
        turno.calcular_total()
        print(f"💰 Total calculado: ${turno.total}")
        
        # Guardar turno (sin validaciones estrictas de horarios por ahora)
        turno.save()
        print(f"✅ Turno guardado con ID: {turno.id}")
        
        # Probar envío de comprobante
        print("📧 Probando envío de comprobante...")
        turno.pagado = True
        turno.enviar_comprobante()  # Llamar directamente al método
        
        print("✅ Comprobante procesado sin errores de encoding")
        
        # Limpiar datos de prueba
        turno.delete()
        print("🧹 Datos de prueba eliminados")
        
        return True
        
    except UnicodeEncodeError as e:
        print(f"❌ Error de encoding: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_system_with_existing_data()
    if success:
        print("\n🎉 ¡Todas las pruebas del sistema pasaron!")
        print("✅ El error de encoding 'ascii' codec can't encode character ha sido solucionado")
    else:
        print("\n❌ Las pruebas del sistema fallaron")
        sys.exit(1)
