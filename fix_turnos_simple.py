#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para asociar turnos existentes a usuarios y corregir datos
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
from GestorSpa.apps.usuarios.models import Perfil, Profesional
from GestorSpa.apps.usuarios.permissions import RoleManager
from GestorSpa.apps.servicios.models import Servicio

def asociar_turnos_a_usuarios():
    """Asociar turnos existentes a usuarios basándose en el email"""
    print("📅 ASOCIANDO TURNOS A USUARIOS")
    print("-" * 35)
    
    # Obtener profesional default
    profesional_default = Profesional.objects.first()
    if not profesional_default:
        print("❌ No hay profesionales en el sistema")
        return
    
    turnos_sin_usuario = Turno.objects.filter(usuario__isnull=True)
    print(f"📊 Turnos sin usuario: {turnos_sin_usuario.count()}")
    
    turnos_procesados = 0
    turnos_asociados = 0
    usuarios_creados = 0
    
    for turno in turnos_sin_usuario:
        turnos_procesados += 1
        print(f"\n🔄 Procesando turno {turno.id} (Email: {turno.email})")
        
        # Buscar usuario por email
        usuario = User.objects.filter(email=turno.email).first()
        
        if not usuario:
            # Crear usuario basado en los datos del turno
            username = turno.email.split('@')[0]
            # Asegurar username único
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}_{counter}"
                counter += 1
            
            try:
                usuario = User.objects.create_user(
                    username=username,
                    email=turno.email,
                    password='temporal123',  # Password temporal
                    first_name=turno.nombre.split()[0] if turno.nombre else 'Cliente',
                    last_name=' '.join(turno.nombre.split()[1:]) if len(turno.nombre.split()) > 1 else ''
                )
                
                # Crear perfil de cliente
                perfil, created = Perfil.objects.get_or_create(
                    usuario=usuario,
                    defaults={'tipo_usuario': 'cliente'}
                )
                usuarios_creados += 1
                print(f"   ✅ Usuario creado: {usuario.username}")
            except Exception as e:
                print(f"   ❌ Error creando usuario: {str(e)}")
                continue
        else:
            print(f"   ✅ Usuario encontrado: {usuario.username}")
        
        # Asociar turno al usuario
        turno.usuario = usuario
        
        # Asegurar que tiene profesional asignado
        if not turno.profesional:
            turno.profesional = profesional_default
        
        # Actualizar datos del turno para consistencia
        turno.email = usuario.email
        if not turno.nombre or turno.nombre.strip() == '':
            turno.nombre = f"{usuario.first_name} {usuario.last_name}".strip() or usuario.username
        
        try:
            turno.save()
            turnos_asociados += 1
            print(f"   ✅ Turno asociado al usuario: {usuario.username}")
        except Exception as e:
            print(f"   ❌ Error guardando turno: {str(e)}")
    
    print(f"\n📈 RESUMEN:")
    print(f"   - Turnos procesados: {turnos_procesados}")
    print(f"   - Turnos asociados: {turnos_asociados}")
    print(f"   - Usuarios creados: {usuarios_creados}")

def verificar_estado_final():
    """Verificar el estado final del sistema"""
    print("\n🎯 VERIFICACIÓN FINAL")
    print("-" * 25)
    
    total_usuarios = User.objects.count()
    usuarios_con_perfil = User.objects.filter(perfil__isnull=False).count()
    
    total_turnos = Turno.objects.count()
    turnos_con_usuario = Turno.objects.filter(usuario__isnull=False).count()
    turnos_con_profesional = Turno.objects.filter(profesional__isnull=False).count()
    
    print(f"👥 Usuarios totales: {total_usuarios}")
    print(f"👥 Usuarios con perfil: {usuarios_con_perfil}")
    print(f"📅 Turnos totales: {total_turnos}")
    print(f"📅 Turnos con usuario: {turnos_con_usuario}")
    print(f"📅 Turnos con profesional: {turnos_con_profesional}")
    
    # Mostrar distribución de roles
    print("\n📊 Distribución de roles:")
    for tipo in ['cliente', 'profesional', 'administrador']:
        count = User.objects.filter(perfil__tipo_usuario=tipo).count()
        print(f"   - {tipo.capitalize()}: {count}")
    
    # Mostrar profesionales
    print(f"\n🏥 Profesionales: {Profesional.objects.count()}")
    for prof in Profesional.objects.all():
        print(f"   - {prof.nombre_completo} ({prof.especialidad})")
    
    if turnos_con_usuario == total_turnos and usuarios_con_perfil == total_usuarios:
        print("\n✅ ¡SISTEMA COMPLETAMENTE CONFIGURADO!")
        return True
    else:
        print("\n⚠️  Sistema parcialmente configurado")
        return False

if __name__ == "__main__":
    try:
        print("🚀 ASOCIANDO TURNOS A USUARIOS")
        print("=" * 40)
        
        # Asociar turnos
        asociar_turnos_a_usuarios()
        
        # Verificar estado final
        if verificar_estado_final():
            print("\n🎉 ¡ASOCIACIÓN COMPLETADA EXITOSAMENTE!")
            print("🔗 Ahora puedes probar el sistema en: http://127.0.0.1:8000/turnos/reservar/")
            print("📝 Todos los turnos están asociados a usuarios únicos")
        else:
            print("\n⚠️  Hay problemas pendientes por revisar")
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        import traceback
        traceback.print_exc()
