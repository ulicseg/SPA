# -*- coding: utf-8 -*-
"""
Script de prueba para verificar el manejo de caracteres especiales en el sistema de reservas
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GestorSpa.configuraciones.settings')
django.setup()

from GestorSpa.apps.turnos.models import Turno
from GestorSpa.apps.servicios.models import Servicio
from GestorSpa.apps.usuarios.models import Profesional
from datetime import date, time, timedelta
from decimal import Decimal

def test_encoding():
    """Prueba el manejo de encoding UTF-8 con caracteres especiales"""
    
    print("=== Prueba de Encoding UTF-8 ===")
    
    # Datos de prueba con caracteres especiales
    test_data = {
        'nombre': 'José María Fernández',
        'email': 'jose.maria@email.com',
        'telefono': '+54 3624 567890',
        'metodo_pago': 'debito'
    }
    
    try:
        # Obtener servicio y profesional para la prueba
        servicio = Servicio.objects.first()
        profesional = Profesional.objects.first()
        
        if not servicio or not profesional:
            print("❌ No hay servicios o profesionales en la base de datos")
            return False
        
        print(f"✅ Servicio: {servicio.nombre}")
        print(f"✅ Profesional: {profesional}")
        
        # Crear turno de prueba
        fecha_prueba = date.today() + timedelta(days=3)
        hora_prueba = time(10, 0)
        
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
        
        # Validar turno
        turno.full_clean()
        print("✅ Validación del turno exitosa")
        
        # Calcular total
        turno.calcular_total()
        print(f"✅ Total calculado: ${turno.total}")
        
        # Guardar turno
        turno.save()
        print(f"✅ Turno guardado con ID: {turno.id}")
        
        # Probar envío de comprobante
        print("📧 Probando envío de comprobante...")
        turno.pagado = True
        turno.save()  # Esto debería disparar el envío del email
        
        print("✅ Todas las pruebas de encoding pasaron exitosamente")
        return True
        
    except UnicodeEncodeError as e:
        print(f"❌ Error de encoding: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error general: {str(e)}")
        return False
    finally:
        # Limpiar datos de prueba
        try:
            if 'turno' in locals() and turno.id:
                turno.delete()
                print("🧹 Datos de prueba eliminados")
        except:
            pass

if __name__ == "__main__":
    success = test_encoding()
    if success:
        print("\n🎉 ¡Todas las pruebas de encoding pasaron!")
    else:
        print("\n❌ Las pruebas de encoding fallaron")
        sys.exit(1)
