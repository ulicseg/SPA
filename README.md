# 🏨 GestorSpa - Sistema de Gestión para Spa

[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Sistema completo de gestión para spa que permite administrar servicios, turnos, profesionales y clientes con un sistema de roles robusto.

## ✨ Características Principales

- 👥 **Sistema de Usuarios Multi-Rol**: Clientes, Profesionales y Administradores
- 📅 **Gestión de Turnos**: Reserva inteligente con disponibilidad en tiempo real
- 💆 **Servicios del Spa**: Catálogo completo con precios y descripciones
- 👨‍⚕️ **Gestión de Profesionales**: Perfiles, especialidades y horarios
- 📧 **Notificaciones por Email**: Confirmaciones automáticas de reservas
- 📊 **Reportes y Estadísticas**: Panel de control con métricas
- � **Interfaz Moderna**: Diseño responsivo con Bootstrap 5
- 🔒 **Seguridad**: Sistema de permisos y autenticación robusto

## 🚀 Instalación y Configuración

> ⚠️ **IMPORTANTE**: Este proyecto no incluye usuarios predeterminados por seguridad. Debes crear tus propios usuarios después de la instalación.

## ⚡ Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/GestorSpa.git
cd GestorSpa

# 2. Crear entorno virtual
python -m venv env
# Windows: env\Scripts\activate
# Linux/Mac: source env/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 5. Ejecutar migraciones
python manage.py migrate

# 6. Crear superusuario (OBLIGATORIO)
python manage.py createsuperuser

# 7. Configurar roles del sistema
python manage.py setup_roles --create-groups

# 8. Ejecutar servidor
python manage.py runserver
```

📱 **¡Listo!** Visita `http://127.0.0.1:8000` para usar la aplicación.

## 📋 Instalación Detallada

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

## Pasos para Instalar y Ejecutar el Proyecto

1. **Clonar el Repositorio**
```bash
git clone <URL_DEL_REPOSITORIO>
cd GestorSpa
```

2. **Crear y Activar Entorno Virtual**
```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/Mac
python3 -m venv env
source env/bin/activate
```

3. **Instalar Dependencias**
```bash
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

8. **Configurar Sistema de Roles**
```bash
# Configurar grupos y permisos
python manage.py setup_roles --create-groups

# Crear usuarios de demostración (opcional)
python manage.py create_demo_users
```

9. **Crear Superusuario (si no usas usuarios demo)**
```bash
python manage.py createsuperuser
```

10. **Ejecutar el Servidor de Desarrollo**
```bash
python manage.py runserver
```

El sitio estará disponible en `http://127.0.0.1:8000/`

## Sistema de Roles Implementado

### 👤 Roles Disponibles

| Rol | Descripción | Permisos |
|-----|-------------|----------|
| **Cliente** | Usuarios que reservan servicios | • Reservar turnos<br>• Ver su historial<br>• Editar perfil |
| **Profesional** | Personal del spa | • Ver turnos asignados<br>• Cambiar estado de turnos<br>• Ver servicios |
| **Administrador** | Gestión completa | • CRUD servicios<br>• CRUD turnos<br>• Gestionar usuarios<br>• Acceso admin |

### 🔑 Configuración de Usuarios

**El sistema NO incluye usuarios predeterminados por seguridad.** Después de la instalación:

1. **Crear Administrador Principal**:
```bash
python manage.py createsuperuser
```

2. **Crear Usuarios Adicionales** (opcional para desarrollo):
   - Accede al panel de administración: `http://127.0.0.1:8000/admin`
   - Ve a "Usuarios" y crea usuarios con los roles necesarios
   - O crea usuarios desde la interfaz de registro del sistema

3. **Asignar Roles**:
```bash
# Listar usuarios existentes
python manage.py setup_roles --show-user-roles

# Asignar rol específico a un usuario
python manage.py setup_roles --assign-role nombre_usuario:cliente
python manage.py setup_roles --assign-role nombre_usuario:profesional
```

> 🛡️ **Seguridad**: Nunca uses contraseñas simples en producción. Siempre cambia las credenciales por defecto.

### 🛠️ Comandos de Gestión de Roles

```bash
# Configurar roles iniciales
python manage.py setup_roles --create-groups

# Listar roles disponibles
python manage.py setup_roles --list-roles

# Asignar rol a usuario existente
python manage.py setup_roles --assign-role username:cliente

# Ver roles de usuarios actuales
python manage.py setup_roles --show-user-roles
```

## Acceso al Sistema

### Login del Sistema
- **URL:** `http://127.0.0.1:8000/login`
- **Usa las credenciales** que creaste con `createsuperuser` o registra nuevos usuarios

### Panel de Administración
- **URL:** `http://127.0.0.1:8000/admin`
- **Usuario:** El superusuario que creaste durante la instalación

## Características Principales

- ✅ **Sistema de roles** con 3 niveles de permisos
- ✅ **Gestión de servicios** del spa
- ✅ **Sistema de reserva** de turnos inteligente
- ✅ **Dashboard personalizado** según rol
- ✅ **Panel de administración** avanzado
- ✅ **Gestión de usuarios** y permisos
- ✅ **Generación de PDFs** para comprobantes
- ✅ **Interfaz responsive** y moderna
- Gestión de clientes

## Estructura del Proyecto

```
GestorSpa/
├── GestorSpa/
│   ├── apps/
│   │   ├── servicios/
│   │   └── turnos/
│   ├── configuraciones/
│   │   └── settings.py
│   └── templates/
├── requirements.txt
├── .env
├── .gitignore
├── manage.py
└── README.md
```

## Solución de Problemas Comunes

1. **Error de Pillow**
```bash
pip install Pillow
```

2. **Error de python-dotenv**
```bash
pip install python-dotenv
```

3. **Error de psycopg2**
```bash
pip install psycopg2
# Si hay error, intentar:
pip install psycopg2-binary
```

4. **Error de conexión a PostgreSQL**
- Verificar que PostgreSQL esté corriendo
- Verificar credenciales en .env
- Verificar que la base de datos exista

## Notas Importantes

- Asegúrate de no compartir tu `SECRET_KEY` ni información sensible
- El archivo settings.py está ignorado en git por seguridad
- Para producción, configura adecuadamente `DEBUG=False`
- Mantén actualizado tu archivo requirements.txt:
```bash
pip freeze > requirements.txt
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **Django 5.2** - Framework web de Python
- **PostgreSQL** - Base de datos principal
- **SQLite** - Base de datos de desarrollo
- **WeasyPrint** - Generación de PDFs

### Frontend
- **Bootstrap 5** - Framework CSS
- **HTML5 & CSS3** - Estructura y estilos
- **JavaScript** - Interactividad

### Herramientas
- **Git** - Control de versiones
- **Python-dotenv** - Gestión de variables de entorno
- **Django Forms** - Validación de datos
- **Django Auth** - Sistema de autenticación

## 📸 Capturas de Pantalla

### Panel de Administración
![Admin Dashboard](docs/images/admin-dashboard.png)

### Sistema de Reservas
![Booking System](docs/images/booking-system.png)

### Gestión de Servicios
![Services Management](docs/images/services-management.png)

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor lee [CONTRIBUTING.md](CONTRIBUTING.md) para conocer el proceso.

1. Fork el proyecto
2. Crea una rama para tu funcionalidad (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 💬 Contacto

- **Proyecto**: [https://github.com/tu-usuario/GestorSpa](https://github.com/tu-usuario/GestorSpa)
- **Issues**: [https://github.com/tu-usuario/GestorSpa/issues](https://github.com/tu-usuario/GestorSpa/issues)

## 🚀 Próximas Funcionalidades

- [ ] Integración con sistemas de pago
- [ ] Notificaciones push
- [ ] API REST para aplicaciones móviles
- [ ] Calendario avanzado con vista semanal/mensual
- [ ] Sistema de descuentos y promociones
- [ ] Integración con redes sociales

---

⭐ **¡Dale una estrella si te gusta el proyecto!** ⭐

