#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para inicializar la base de datos con datos de demo
para el sistema de reservas por usuario único
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, 'c:/Users/UliEl/OneDrive/Desktop/Proyectos/GESTORSPA/SPA')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GestorSpa.configuraciones.settings')

import django
django.setup()

from django.contrib.auth.models import User
from GestorSpa.apps.usuarios.models import Perfil, Profesional
from GestorSpa.apps.servicios.models import Servicio
from GestorSpa.apps.turnos.models import Turno
from datetime import date, time

def crear_usuarios_demo():
    """Crear usuarios de demo con perfiles"""
    print("👥 CREANDO USUARIOS DE DEMO")
    print("-" * 30)
    
    usuarios = [
        {
            'username': 'admin',
            'email': 'admin@spa.com',
            'password': 'admin123',
            'first_name': 'Admin',
            'last_name': 'SPA',
            'tipo': 'administrador',
            'is_staff': True,
            'is_superuser': True
        },
        {
            'username': 'profesional1',
            'email': 'profesional@spa.com',
            'password': 'prof123',
            'first_name': 'Dr. María',
            'last_name': 'González',
            'tipo': 'profesional'
        },
        {
            'username': 'cliente1',
            'email': 'cliente1@spa.com',
            'password': 'cliente123',
            'first_name': 'Ana',
            'last_name': 'López',
            'tipo': 'cliente'
        },
        {
            'username': 'cliente2',
            'email': 'cliente2@spa.com',
            'password': 'cliente123',
            'first_name': 'Juan',
            'last_name': 'Pérez',
            'tipo': 'cliente'
        }
    ]
    
    for user_data in usuarios:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'email': user_data['email'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'is_staff': user_data.get('is_staff', False),
                'is_superuser': user_data.get('is_superuser', False)
            }
        )
        
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"✅ Usuario creado: {user.username}")
        else:
            print(f"✅ Usuario existente: {user.username}")
        
        # Crear perfil
        perfil, created = Perfil.objects.get_or_create(
            usuario=user,
            defaults={'tipo_usuario': user_data['tipo']}
        )
        
        if created:
            print(f"   📋 Perfil creado: {user_data['tipo']}")

def crear_servicios_demo():
    """Crear servicios de demo"""
    print("\n🏥 CREANDO SERVICIOS DE DEMO")
    print("-" * 30)
    
    servicios = [
        {
            'nombre': 'Masaje Relajante',
            'descripcion': 'Masaje corporal completo para relajar músculos y mente',
            'duracion': 60,
            'precio': 8000
        },
        {
            'nombre': 'Facial Hidratante',
            'descripcion': 'Tratamiento facial con productos naturales',
            'duracion': 45,
            'precio': 6000
        },
        {
            'nombre': 'Aromaterapia',
            'descripcion': 'Sesión de relajación con aceites esenciales',
            'duracion': 30,
            'precio': 4000
        },
        {
            'nombre': 'Masaje Descontracturante',
            'descripcion': 'Masaje terapéutico para aliviar contracturas',
            'duracion': 90,
            'precio': 12000
        }
    ]
    
    for servicio_data in servicios:
        servicio, created = Servicio.objects.get_or_create(
            nombre=servicio_data['nombre'],
            defaults=servicio_data
        )
        
        if created:
            print(f"✅ Servicio creado: {servicio.nombre}")
        else:
            print(f"✅ Servicio existente: {servicio.nombre}")

def crear_profesional_demo():
    """Crear profesional de demo"""
    print("\n👩‍⚕️ CREANDO PROFESIONAL DE DEMO")
    print("-" * 30)
    
    user_profesional = User.objects.get(username='profesional1')
    
    profesional, created = Profesional.objects.get_or_create(
        usuario=user_profesional,
        defaults={
            'nombre_completo': f"{user_profesional.first_name} {user_profesional.last_name}",
            'especialidad': 'Terapia y Relajación',
            'numero_matricula': 'SPA-001',
            'contacto': user_profesional.email,
            'fecha_inicio': date.today(),
            'estado': 'activo',
            'biografia': 'Especialista en terapias de relajación y masajes terapéuticos.'
        }
    )
    
    if created:
        print(f"✅ Profesional creado: {profesional.nombre_completo}")
    else:
        print(f"✅ Profesional existente: {profesional.nombre_completo}")
    
    return profesional

def verificar_sistema():
    """Verificar que el sistema esté listo"""
    print("\n🔍 VERIFICANDO SISTEMA")
    print("-" * 25)
    
    print(f"👥 Usuarios: {User.objects.count()}")
    print(f"📋 Perfiles: {Perfil.objects.count()}")
    print(f"🏥 Servicios: {Servicio.objects.count()}")
    print(f"👩‍⚕️ Profesionales: {Profesional.objects.count()}")
    print(f"📅 Turnos: {Turno.objects.count()}")
    
    print("\n📊 Usuarios por tipo:")
    for tipo in ['cliente', 'profesional', 'administrador']:
        count = User.objects.filter(perfil__tipo_usuario=tipo).count()
        print(f"   - {tipo.capitalize()}: {count}")
    
    print("\n✅ Sistema listo para usar!")
    print("🔗 URLs importantes:")
    print("   - Reservar turno: http://127.0.0.1:8000/turnos/reservar/")
    print("   - Registro cliente: http://127.0.0.1:8000/usuarios/registro-cliente/")
    print("   - Login: http://127.0.0.1:8000/login/")
    print("   - Admin: http://127.0.0.1:8000/admin/")
    print("\n🔐 Credenciales de prueba:")
    print("   - Admin: admin / admin123")
    print("   - Profesional: profesional1 / prof123")
    print("   - Cliente 1: cliente1 / cliente123")
    print("   - Cliente 2: cliente2 / cliente123")

if __name__ == "__main__":
    try:
        print("🚀 INICIALIZANDO SISTEMA DE RESERVAS POR USUARIO ÚNICO")
        print("=" * 65)
        
        crear_usuarios_demo()
        crear_servicios_demo()
        crear_profesional_demo()
        verificar_sistema()
        
        print("\n🎉 ¡SISTEMA INICIALIZADO EXITOSAMENTE!")
        print("\n📝 CARACTERÍSTICAS IMPLEMENTADAS:")
        print("   ✅ Solo usuarios registrados pueden reservar")
        print("   ✅ Turnos asociados por username único")
        print("   ✅ Registro automático como cliente")
        print("   ✅ Login obligatorio para reservas")
        print("   ✅ Base de datos limpia y nueva")
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        import traceback
        traceback.print_exc()
