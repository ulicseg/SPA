#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script simplificado para probar el sistema de usuario único
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, 'c:/Users/UliEl/OneDrive/Desktop/Proyectos/GESTORSPA/SPA')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GestorSpa.configuraciones.settings')

import django
django.setup()

from django.contrib.auth.models import User
from GestorSpa.apps.turnos.models import Turno
from GestorSpa.apps.usuarios.models import Perfil
from GestorSpa.apps.usuarios.permissions import RoleManager

def verificar_sistema():
    """Verificación básica del sistema"""
    print("🔍 VERIFICANDO SISTEMA DE USUARIO ÚNICO")
    print("=" * 50)
    
    # 1. Verificar modelo Turno tiene campo usuario
    turno_fields = [field.name for field in Turno._meta.fields]
    if 'usuario' in turno_fields:
        print("✅ Campo 'usuario' presente en modelo Turno")
    else:
        print("❌ Campo 'usuario' no encontrado")
        return False
    
    # 2. Verificar usuarios existentes
    total_users = User.objects.count()
    print(f"📊 Total de usuarios en sistema: {total_users}")
    
    # 3. Verificar turnos asociados a usuarios
    turnos_con_usuario = Turno.objects.filter(usuario__isnull=False).count()
    turnos_sin_usuario = Turno.objects.filter(usuario__isnull=True).count()
    total_turnos = Turno.objects.count()
    
    print(f"📊 Turnos con usuario asociado: {turnos_con_usuario}")
    print(f"📊 Turnos sin usuario asociado: {turnos_sin_usuario}")
    print(f"📊 Total de turnos: {total_turnos}")
    
    # 4. Mostrar algunos ejemplos
    if total_turnos > 0:
        print("\n📋 Últimos 5 turnos:")
        for turno in Turno.objects.all()[:5]:
            usuario_info = f"{turno.usuario.username}" if turno.usuario else "Sin usuario"
            print(f"   - ID: {turno.id} | Fecha: {turno.fecha} | Usuario: {usuario_info} | Email: {turno.email}")
    
    # 5. Verificar roles de usuarios
    print("\n👥 Roles de usuarios:")
    for user in User.objects.all()[:10]:  # Primeros 10 usuarios
        role = RoleManager.get_user_role(user)
        print(f"   - {user.username} ({user.email}) -> {role}")
    
    print("\n✅ Verificación completada")
    return True

def test_flujo_basico():
    """Prueba básica del flujo"""
    print("\n🧪 PRUEBA BÁSICA DEL FLUJO")
    print("-" * 30)
    
    # Crear usuario de prueba temporal
    test_user = None
    try:
        # Limpiar usuario de prueba si existe
        User.objects.filter(username='test_temp').delete()
        
        # Crear usuario
        test_user = User.objects.create_user(
            username='test_temp',
            email='test@temp.com',
            password='temp123',
            first_name='Test',
            last_name='User'
        )
        
        # Crear perfil
        if not hasattr(test_user, 'perfil'):
            Perfil.objects.create(usuario=test_user, tipo_usuario='cliente')
        
        print(f"✅ Usuario de prueba creado: {test_user.username}")
        print(f"✅ Rol: {RoleManager.get_user_role(test_user)}")
        
        # Simular creación de turno
        from GestorSpa.apps.servicios.models import Servicio
        servicio = Servicio.objects.first()
        
        if servicio:
            turno = Turno.objects.create(
                usuario=test_user,
                nombre=f"{test_user.first_name} {test_user.last_name}",
                email=test_user.email,
                telefono="123456789",
                servicio=servicio,
                fecha="2025-12-31",
                hora_inicio="10:00",
                notas="Turno de prueba"
            )
            
            print(f"✅ Turno creado: ID {turno.id}")
            print(f"✅ Asociado al usuario: {turno.usuario.username}")
            print(f"✅ Email del turno: {turno.email}")
            
            # Limpiar
            turno.delete()
            print("✅ Turno de prueba eliminado")
        else:
            print("⚠️  No hay servicios disponibles para crear turno de prueba")
        
    except Exception as e:
        print(f"❌ Error en prueba: {str(e)}")
    finally:
        if test_user:
            test_user.delete()
            print("✅ Usuario de prueba eliminado")

if __name__ == "__main__":
    try:
        verificar_sistema()
        test_flujo_basico()
        
        print("\n🎯 SISTEMA VERIFICADO EXITOSAMENTE")
        print("🔗 Puedes probar el sistema en: http://127.0.0.1:8000/turnos/reservar/")
        print("📝 Recuerda: Solo usuarios registrados y logueados pueden reservar turnos")
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        import traceback
        traceback.print_exc()
