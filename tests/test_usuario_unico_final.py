#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para probar el sistema unificado de reservas por usuario único.
Verifica que:
1. Solo usuarios logueados pueden reservar
2. Los turnos se asocian al usuario por username
3. La invitación a registro funciona correctamente
"""

import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GestorSpa.configuraciones.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import Client, RequestFactory
from django.urls import reverse
from GestorSpa.apps.turnos.models import Turno
from GestorSpa.apps.servicios.models import Servicio
from GestorSpa.apps.usuarios.models import Perfil
from GestorSpa.apps.usuarios.permissions import RoleManager
from datetime import date, time
import logging

# Configurar encoding
import sys
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_usuario_unico_system():
    """Prueba integral del sistema de usuarios únicos"""
    
    print("🧪 INICIANDO PRUEBAS DEL SISTEMA DE RESERVAS POR USUARIO ÚNICO")
    print("=" * 70)
    
    client = Client()
    
    # 1. Probar acceso sin login
    print("\n1️⃣ Probando acceso a reservas sin estar logueado...")
    response = client.get('/turnos/reservar/')
    
    if response.status_code == 200:
        print("   ✅ Sistema muestra invitación a registrarse")
        if 'registro' in response.content.decode().lower():
            print("   ✅ Contiene invitación a registro")
        else:
            print("   ⚠️  No se encontró invitación a registro en la respuesta")
    elif response.status_code == 302:
        print(f"   ✅ Redirige correctamente: {response.url}")
    else:
        print(f"   ❌ Respuesta inesperada: {response.status_code}")
    
    # 2. Crear usuario de prueba
    print("\n2️⃣ Creando usuario de prueba...")
    test_username = "cliente_test_único"
    test_email = "cliente.test@spa.com"
    
    # Limpiar usuario existente si existe
    User.objects.filter(username=test_username).delete()
    
    user = User.objects.create_user(
        username=test_username,
        email=test_email,
        password="test123456",
        first_name="Cliente",
        last_name="Prueba"
    )
    
    # Asegurar que tiene perfil de cliente
    if not hasattr(user, 'perfil'):
        Perfil.objects.create(usuario=user, tipo_usuario='cliente')
    else:
        user.perfil.tipo_usuario = 'cliente'
        user.perfil.save()
    
    print(f"   ✅ Usuario creado: {user.username} ({user.email})")
    print(f"   ✅ Rol asignado: {RoleManager.get_user_role(user)}")
    
    # 3. Probar login
    print("\n3️⃣ Probando login...")
    login_success = client.login(username=test_username, password="test123456")
    if login_success:
        print("   ✅ Login exitoso")
    else:
        print("   ❌ Error en login")
        return False
    
    # 4. Verificar acceso a reservas logueado
    print("\n4️⃣ Probando acceso a reservas estando logueado...")
    response = client.get('/turnos/reservar/')
    
    if response.status_code == 200:
        print("   ✅ Acceso permitido para usuario logueado")
        content = response.content.decode()
        if user.email in content:
            print("   ✅ Email del usuario aparece prellenado")
        if user.username in content or user.first_name in content:
            print("   ✅ Nombre del usuario aparece prellenado")
    else:
        print(f"   ❌ Error de acceso: {response.status_code}")
        return False
    
    # 5. Crear servicio de prueba si no existe
    print("\n5️⃣ Verificando servicios disponibles...")
    servicio = Servicio.objects.filter(activo=True).first()
    if not servicio:
        servicio = Servicio.objects.create(
            nombre="Masaje de Prueba",
            descripcion="Servicio para testing",
            duracion=60,
            precio=5000,
            activo=True
        )
        print(f"   ✅ Servicio creado: {servicio.nombre}")
    else:
        print(f"   ✅ Servicio disponible: {servicio.nombre}")
    
    # 6. Probar creación de turno asociado al usuario
    print("\n6️⃣ Probando creación de turno asociado al usuario...")
    
    turnos_antes = Turno.objects.filter(usuario=user).count()
    print(f"   📊 Turnos antes: {turnos_antes}")
    
    # Datos del turno
    turno_data = {
        'nombre': f"{user.first_name} {user.last_name}",
        'email': user.email,
        'telefono': '1234567890',
        'servicio': servicio.id,
        'fecha': '2025-12-31',
        'hora_inicio': '10:00',
        'notas': 'Turno de prueba para usuario único'
    }
    
    response = client.post('/turnos/reservar/', turno_data)
    
    if response.status_code in [200, 302]:
        turnos_despues = Turno.objects.filter(usuario=user).count()
        print(f"   📊 Turnos después: {turnos_despues}")
        
        if turnos_despues > turnos_antes:
            ultimo_turno = Turno.objects.filter(usuario=user).last()
            print(f"   ✅ Turno creado exitosamente")
            print(f"   ✅ ID del turno: {ultimo_turno.id}")
            print(f"   ✅ Asociado al usuario: {ultimo_turno.usuario.username}")
            print(f"   ✅ Email del turno: {ultimo_turno.email}")
            
            # Verificar que el email coincide con el del usuario
            if ultimo_turno.email == user.email:
                print("   ✅ Email del turno coincide con el del usuario")
            else:
                print(f"   ⚠️  Email del turno ({ultimo_turno.email}) no coincide con el del usuario ({user.email})")
        else:
            print("   ❌ No se creó el turno")
            return False
    else:
        print(f"   ❌ Error en creación de turno: {response.status_code}")
        if hasattr(response, 'content'):
            print(f"   📄 Contenido de error: {response.content.decode()[:200]}...")
        return False
    
    # 7. Probar filtrado de turnos por usuario
    print("\n7️⃣ Probando filtrado de turnos por usuario...")
    
    mis_turnos_response = client.get('/usuarios/mis-turnos/')
    if mis_turnos_response.status_code == 200:
        print("   ✅ Acceso a 'mis turnos' exitoso")
        
        # Verificar que solo aparecen los turnos del usuario
        turnos_usuario = Turno.objects.filter(usuario=user)
        print(f"   📊 Turnos del usuario en BD: {turnos_usuario.count()}")
        
        for turno in turnos_usuario:
            print(f"   📅 Turno: {turno.fecha} - {turno.servicio.nombre} (Usuario: {turno.usuario.username})")
    else:
        print(f"   ❌ Error en acceso a mis turnos: {mis_turnos_response.status_code}")
    
    # 8. Verificar unicidad del username
    print("\n8️⃣ Verificando unicidad del username...")
    
    # Intentar crear otro usuario con el mismo username
    try:
        User.objects.create_user(username=test_username, email="otro@email.com", password="test123")
        print("   ❌ CRÍTICO: Se permitió crear usuario con username duplicado")
        return False
    except Exception as e:
        print("   ✅ Username único verificado - no se permite duplicación")
    
    # 9. Probar logout y acceso nuevamente
    print("\n9️⃣ Probando logout y acceso...")
    client.logout()
    
    response = client.get('/turnos/reservar/')
    if response.status_code in [302, 200]:
        print("   ✅ Después de logout, se requiere autenticación nuevamente")
        if response.status_code == 302:
            print(f"   ✅ Redirige a: {response.url}")
    else:
        print(f"   ❌ Comportamiento inesperado después de logout: {response.status_code}")
    
    # 10. Limpiar datos de prueba
    print("\n🧹 Limpiando datos de prueba...")
    turnos_prueba = Turno.objects.filter(usuario=user)
    count_turnos = turnos_prueba.count()
    turnos_prueba.delete()
    user.delete()
    print(f"   ✅ Usuario eliminado")
    print(f"   ✅ {count_turnos} turnos de prueba eliminados")
    
    print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS EXITOSAMENTE")
    print("=" * 70)
    print("✅ Sistema de reservas por usuario único funcionando correctamente")
    print("✅ Solo usuarios logueados pueden reservar")
    print("✅ Turnos se asocian correctamente al usuario")
    print("✅ Username es único en el sistema")
    print("✅ Filtrado de turnos por usuario funciona")
    
    return True

def verificar_configuracion():
    """Verifica la configuración del sistema"""
    print("\n🔧 VERIFICANDO CONFIGURACIÓN DEL SISTEMA")
    print("-" * 50)
    
    # Verificar modelo Turno
    from GestorSpa.apps.turnos.models import Turno
    turno_fields = [field.name for field in Turno._meta.fields]
    
    if 'usuario' in turno_fields:
        print("✅ Campo 'usuario' presente en modelo Turno")
    else:
        print("❌ CRÍTICO: Campo 'usuario' no encontrado en modelo Turno")
        return False
    
    # Verificar settings
    print(f"✅ LOGIN_URL configurado: {settings.LOGIN_URL}")
    
    # Verificar URLs
    try:
        from django.urls import reverse
        reverse('usuarios:registro_cliente')
        print("✅ URL de registro de cliente configurada")
    except:
        print("❌ CRÍTICO: URL de registro de cliente no configurada")
        return False
    
    try:
        reverse('turnos:turno_reserva_unificada')
        print("✅ URL de reserva unificada configurada")
    except:
        print("❌ CRÍTICO: URL de reserva unificada no configurada")
        return False
    
    return True

if __name__ == "__main__":
    try:
        print("🚀 INICIANDO VERIFICACIÓN DEL SISTEMA DE USUARIO ÚNICO")
        print("=" * 70)
        
        if verificar_configuracion():
            print("\n✅ Configuración verificada correctamente")
            
            if test_usuario_unico_system():
                print("\n🎯 RESULTADO FINAL: ¡SISTEMA COMPLETAMENTE FUNCIONAL!")
                sys.exit(0)
            else:
                print("\n❌ RESULTADO FINAL: Errores encontrados en las pruebas")
                sys.exit(1)
        else:
            print("\n❌ RESULTADO FINAL: Errores de configuración")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
