#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corregir los tipos de usuario
"""

import sys
import os

sys.path.insert(0, 'c:/Users/UliEl/OneDrive/Desktop/Proyectos/GESTORSPA/SPA')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GestorSpa.configuraciones.settings')

import django
django.setup()

from django.contrib.auth.models import User
from GestorSpa.apps.usuarios.models import Perfil

# Corregir tipos de usuario
admin_user = User.objects.get(username='admin')
admin_user.perfil.tipo_usuario = 'administrador'
admin_user.perfil.save()

prof_user = User.objects.get(username='profesional1')
prof_user.perfil.tipo_usuario = 'profesional'
prof_user.perfil.save()

print("✅ Perfiles corregidos")
print(f"Admin: {admin_user.perfil.tipo_usuario}")
print(f"Profesional: {prof_user.perfil.tipo_usuario}")
