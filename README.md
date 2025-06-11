# 🌸 GestorSpa - Sistema de Gestión Integral para Spa

Sistema de gestión completo para spa con sistema de roles avanzado, que permite administrar servicios, turnos, clientes y personal con diferentes niveles de acceso.

## ✨ Características Principales

- 🔐 **Sistema de Roles Avanzado**: Cliente, Profesional y Administrador
- 📅 **Gestión de Turnos**: Reserva y administración de citas
- 💆‍♀️ **Gestión de Servicios**: CRUD completo de servicios del spa
- 👥 **Gestión de Usuarios**: Panel de administración de clientes y personal
- 📊 **Dashboards Personalizados**: Diferentes vistas según el rol del usuario
- 🎨 **Interfaz Moderna**: Diseño responsive con Tailwind CSS
- 📱 **Navegación Inteligente**: Menús adaptativos según permisos
- 🔒 **Sistema de Permisos**: Protección de vistas y funcionalidades

## 👥 Roles del Sistema

### 🛍️ CLIENTE
- Reservar y gestionar sus propios turnos
- Ver historial de citas
- Editar perfil personal
- Dashboard con estadísticas personales

### 💼 PROFESIONAL
- Ver turnos asignados
- Consultar información de servicios
- Dashboard con agenda del día
- Gestión de perfil

### 👑 ADMINISTRADOR
- Control total del sistema
- Gestión completa de usuarios y roles
- CRUD de servicios y turnos
- Panel administrativo de Django
- Dashboard con estadísticas generales

## 🔐 Usuarios de Prueba

Para probar el sistema, puedes usar estos usuarios predefinidos:

### 👑 Administrador
- **Usuario**: `ana_felicidad`
- **Contraseña**: `admin123`
- **Email**: `ana@spa.com`
- **Acceso**: Control total del sistema

### 💼 Profesional
- **Usuario**: `maria_profesional`
- **Contraseña**: `prof123`
- **Email**: `maria@spa.com`
- **Acceso**: Ver turnos asignados y servicios

### 🛍️ Cliente
- **Usuario**: `juan_cliente`
- **Contraseña**: `cliente123`
- **Email**: `juan@cliente.com`
- **Acceso**: Reservar turnos y gestionar perfil

## 📋 Requisitos Previos

1. **Instalar Python**
   - Descargar Python 3.8 o superior desde [python.org](https://www.python.org/downloads/)
   - Durante la instalación, marcar la opción "Add Python to PATH"
   - Verificar la instalación:
     ```bash
     python --version
     ```

2. **Instalar Git**
   - Descargar Git desde [git-scm.com](https://git-scm.com/downloads)
   - Verificar la instalación:
     ```bash
     git --version
     ```

3. **Instalar PostgreSQL**
   - Descargar PostgreSQL desde [postgresql.org](https://www.postgresql.org/download/)
   - Durante la instalación, anotar la contraseña del usuario postgres
   - Verificar la instalación:
     ```bash
     psql --version
     ```

## 🚀 Instalación Rápida

### Opción 1: Con SQLite (Recomendado para desarrollo)

1. **Clonar el Repositorio**
```bash
git clone <URL_DEL_REPOSITORIO>
cd GestorSpa
```

2. **Crear y Activar Entorno Virtual**
```bash
# Windows
python -m venv entorno
entorno\Scripts\activate

# Linux/Mac
python3 -m venv entorno
source entorno/bin/activate
```

3. **Instalar Dependencias**
```bash
pip install -r requirements.txt
```

4. **Realizar Migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Configurar Sistema de Roles y Usuarios de Prueba**
```bash
python manage.py setup_groups
python manage.py crear_usuarios_ejemplo
```

6. **Ejecutar el Servidor**
```bash
python manage.py runserver
```

¡Listo! El sitio estará disponible en `http://127.0.0.1:8000/`

### Opción 2: Con PostgreSQL (Para producción)
pip install -r requirements.txt
```

4. **Configurar Base de Datos**
```bash
# Acceder a PostgreSQL
psql -U postgres

# Crear base de datos
CREATE DATABASE gestorspa;
\q
```

5. **Configurar Variables de Entorno**
- Crear archivo `.env` en la raíz del proyecto
- Copiar el contenido siguiente y modificar según tus datos:
```env
# Django Settings
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=True

# Database Settings
DB_NAME=gestorspa
DB_USER=postgres
DB_PASSWORD=tu_contraseña_postgres
DB_HOST=localhost
DB_PORT=5432

# Email Settings (opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_app
```

6. **Configurar settings.py**
- Ubicar el archivo `GestorSpa/configuraciones/settings.py`
- Agregar las siguientes importaciones al inicio:
```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
```

- Modificar la configuración de SECRET_KEY:
```python
SECRET_KEY = os.getenv('SECRET_KEY')
```

- Modificar la configuración de DEBUG:
```python
DEBUG = os.getenv('DEBUG') == 'True'
```

- Modificar la configuración de la base de datos:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
```

7. **Realizar Migraciones**
```bash
python manage.py makemigrations
python manage.py migrate
```

8. **Crear Superusuario**
```bash
python manage.py createsuperuser
```

9. **Ejecutar el Servidor de Desarrollo**
```bash
python manage.py runserver
```

El sitio estará disponible en `http://127.0.0.1:8000/`

## Acceso al Admin

1. Acceder a `http://127.0.0.1:8000/admin`
2. Ingresar con las credenciales del superusuario creado

## 📱 Funcionalidades por Rol

### 🛍️ Dashboard Cliente
- ✅ Resumen de turnos próximos
- ✅ Historial de citas
- ✅ Reserva rápida de turnos
- ✅ Estadísticas personales
- ✅ Edición de perfil

### 💼 Dashboard Profesional
- ✅ Turnos asignados para hoy
- ✅ Próximas citas programadas
- ✅ Lista de servicios disponibles
- ✅ Información de contacto de clientes
- ✅ Edición de perfil

### 👑 Dashboard Administrador
- ✅ Estadísticas generales del spa
- ✅ Gestión completa de usuarios
- ✅ CRUD de servicios y turnos
- ✅ Panel administrativo de Django
- ✅ Control total del sistema

## 🏗️ Estructura del Proyecto

```
GestorSpa/
├── GestorSpa/
│   ├── apps/
│   │   ├── servicios/          # Gestión de servicios
│   │   ├── turnos/             # Sistema de reservas
│   │   ├── usuarios/           # Sistema de roles y usuarios
│   │   └── clientes/           # Gestión de clientes
│   ├── configuraciones/
│   │   └── settings.py         # Configuración Django
│   ├── templates/              # Templates HTML
│   │   ├── auth/              # Login/Registro
│   │   ├── base/              # Base templates
│   │   ├── usuarios/          # Dashboards por rol
│   │   ├── servicios/         # CRUD servicios
│   │   └── turnos/            # Sistema de turnos
│   ├── static/                # Archivos estáticos
│   └── media/                 # Archivos subidos
├── entorno/                   # Entorno virtual
├── requirements.txt           # Dependencias
├── .env                      # Variables de entorno
├── .gitignore               # Archivos ignorados
├── manage.py                # Comando Django
├── README.md               # Documentación
└── SISTEMA_ROLES_DOCUMENTACION.md  # Doc. detallada del sistema
```

## ❓ Solución de Problemas Comunes

### Error de Dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Error de Migraciones
```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

### Recrear Usuarios de Prueba
```bash
python manage.py crear_usuarios_ejemplo
```

### Configurar Grupos y Permisos
```bash
python manage.py setup_groups
```

## 🔧 Comandos de Gestión Personalizados

- `python manage.py setup_groups` - Configura grupos y permisos
- `python manage.py crear_usuarios_ejemplo` - Crea usuarios de prueba
- `python manage.py collectstatic` - Recopila archivos estáticos

## 📚 Documentación Adicional

Para información detallada sobre el sistema de roles, consulta: `SISTEMA_ROLES_DOCUMENTACION.md`

## 🚀 Deploy en Producción

### Configuraciones Importantes
```python
# En settings.py para producción
DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com', 'www.tu-dominio.com']
```

### Variables de Entorno de Producción
```env
DEBUG=False
SECRET_KEY=tu_clave_secreta_muy_segura
DB_NAME=gestorspa_prod
DB_USER=usuario_prod
DB_PASSWORD=contraseña_segura
```

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 👨‍💻 Desarrollado por

**GestorSpa Team** - Sistema completo de gestión para spa con roles avanzados

---

⭐ Si te gusta este proyecto, ¡no olvides darle una estrella en GitHub!

