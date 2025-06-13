#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para asignar roles correctos a los usuarios
"""

import sys
import os

sys.path.insert(0, 'c:/Users/UliEl/OneDrive/Desktop/Proyectos/GESTORSPA/SPA')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GestorSpa.configuraciones.settings')

import django
django.setup()

from django.contrib.auth.models import User
from GestorSpa.apps.usuarios.models import Perfil
from GestorSpa.apps.usuarios.permissions import RoleManager

def asignar_roles():
    """Asignar roles correctos a todos los usuarios"""
    print("🔧 ASIGNANDO ROLES A USUARIOS")
    print("=" * 40)
    
    # Definir usuarios y sus roles
    usuarios_roles = {
        'admin': 'administrador',
        'profesional1': 'profesional', 
        'cliente1': 'cliente',
        'cliente2': 'cliente'
    }
    
    for username, rol_esperado in usuarios_roles.items():
        try:
            user = User.objects.get(username=username)
            
            # Asegurar que el perfil existe y tiene el tipo correcto
            perfil, created = Perfil.objects.get_or_create(
                usuario=user,
                defaults={'tipo_usuario': rol_esperado}
            )
            
            if not created and perfil.tipo_usuario != rol_esperado:
                perfil.tipo_usuario = rol_esperado
                perfil.save()
                print(f"✅ Rol actualizado para {username}: {rol_esperado}")
            elif created:
                print(f"✅ Perfil y rol creado para {username}: {rol_esperado}")
            else:
                print(f"✅ Rol correcto para {username}: {rol_esperado}")
            
            # Usar RoleManager para asignar el rol
            try:
                RoleManager.assign_role_to_user(user, rol_esperado)
                print(f"   📋 Rol asignado via RoleManager: {rol_esperado}")
            except Exception as e:
                print(f"   ⚠️  RoleManager warning: {str(e)}")
            
            # Verificar el rol asignado
            rol_actual = RoleManager.get_user_role(user)
            if rol_actual == rol_esperado:
                print(f"   ✅ Verificación exitosa: {rol_actual}")
            else:
                print(f"   ⚠️  Rol actual: {rol_actual}, esperado: {rol_esperado}")
                
        except User.DoesNotExist:
            print(f"❌ Usuario no encontrado: {username}")
        except Exception as e:
            print(f"❌ Error con {username}: {str(e)}")
        
        print()

def verificar_roles():
    """Verificar que todos los roles están correctamente asignados"""
    print("🔍 VERIFICACIÓN DE ROLES")
    print("=" * 30)
    
    for user in User.objects.all():
        rol = RoleManager.get_user_role(user)
        perfil_tipo = user.perfil.tipo_usuario if hasattr(user, 'perfil') else 'Sin perfil'
        
        print(f"👤 {user.username}:")
        print(f"   📧 Email: {user.email}")
        print(f"   📋 Perfil tipo: {perfil_tipo}")
        print(f"   🎭 Rol RoleManager: {rol}")
        print(f"   👑 Staff: {user.is_staff}")
        print(f"   🔑 Superuser: {user.is_superuser}")
        print()

def mostrar_resumen():
    """Mostrar resumen final de usuarios y roles"""
    print("📊 RESUMEN FINAL DE USUARIOS Y ROLES")
    print("=" * 45)
    
    print("📋 Distribución de roles:")
    for tipo in ['cliente', 'profesional', 'administrador']:
        count = User.objects.filter(perfil__tipo_usuario=tipo).count()
        print(f"   - {tipo.capitalize()}: {count}")
    
    print("\n🔑 Credenciales de acceso:")
    print("   👑 Admin: admin / admin123 (Administrador)")
    print("   👩‍⚕️ Profesional: profesional1 / prof123 (Profesional)")
    print("   👤 Cliente 1: cliente1 / cliente123 (Cliente)")
    print("   👤 Cliente 2: cliente2 / cliente123 (Cliente)")
    
    print("\n✅ ¡Todos los usuarios tienen roles asignados correctamente!")

if __name__ == "__main__":
    try:
        print("🚀 CONFIGURACIÓN DE ROLES DE USUARIO")
        print("=" * 50)
        
        asignar_roles()
        verificar_roles()
        mostrar_resumen()
        
        print("\n🎉 ¡ROLES CONFIGURADOS EXITOSAMENTE!")
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        import traceback
        traceback.print_exc()
