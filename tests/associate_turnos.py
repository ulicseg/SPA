# -*- coding: utf-8 -*-
"""
Script para asociar turnos existentes con usuarios por email
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GestorSpa.configuraciones.settings')
django.setup()

from django.contrib.auth.models import User
from GestorSpa.apps.turnos.models import Turno

def asociar_turnos_con_usuarios():
    """Asocia los turnos existentes con usuarios que tengan el mismo email"""
    
    print("=== Asociando Turnos Existentes con Usuarios ===")
    
    # Obtener turnos sin usuario asociado
    turnos_sin_usuario = Turno.objects.filter(usuario__isnull=True)
    total_turnos = turnos_sin_usuario.count()
    
    print(f"📋 Turnos sin usuario asociado: {total_turnos}")
    
    turnos_asociados = 0
    
    for turno in turnos_sin_usuario:
        try:
            # Buscar usuario con el mismo email
            usuario = User.objects.filter(email=turno.email).first()
            
            if usuario:
                turno.usuario = usuario
                turno.save()
                turnos_asociados += 1
                print(f"✅ Turno ID {turno.id} asociado con usuario {usuario.username}")
            else:
                print(f"⚠️  No se encontró usuario para email: {turno.email}")
                
        except Exception as e:
            print(f"❌ Error asociando turno ID {turno.id}: {str(e)}")
    
    print(f"\n📊 Resumen:")
    print(f"   - Total de turnos procesados: {total_turnos}")
    print(f"   - Turnos asociados exitosamente: {turnos_asociados}")
    print(f"   - Turnos sin asociar: {total_turnos - turnos_asociados}")
    
    return turnos_asociados > 0

if __name__ == "__main__":
    success = asociar_turnos_con_usuarios()
    if success:
        print("\n🎉 ¡Asociación de turnos completada!")
    else:
        print("\n⚠️  No se asociaron turnos (puede ser normal si no hay coincidencias)")
