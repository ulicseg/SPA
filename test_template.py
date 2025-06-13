import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GestorSpa.settings')
django.setup()

from django.template import Template, Context
from django.contrib.auth.models import User
from GestorSpa.apps.usuarios.permissions import RoleManager

# Test simple de la lógica condicional
template_content = """
{% if user_role == 'cliente' %}
    <p>CLIENTE DETECTADO</p>
{% elif user_role == 'profesional' %}
    <p>PROFESIONAL DETECTADO</p>
{% elif user_role == 'administrador' %}
    <p>ADMINISTRADOR DETECTADO</p>
    <div>Dashboard de admin aquí</div>
{% else %}
    <p>SIN ROL</p>
{% endif %}
"""

# Obtener usuario admin
user = User.objects.get(username='admin')
user_role = RoleManager.get_user_role(user)

print(f"User role obtenido: '{user_role}'")
print(f"Tipo de user_role: {type(user_role)}")

# Crear contexto
context = Context({
    'user_role': user_role,
})

# Renderizar template
template = Template(template_content)
result = template.render(context)

print("Resultado del template:")
print(result)

# Test adicional: verificar comparación directa
print(f"\nComparaciones directas:")
print(f"user_role == 'administrador': {user_role == 'administrador'}")
print(f"user_role == 'cliente': {user_role == 'cliente'}")
print(f"user_role == 'profesional': {user_role == 'profesional'}")
