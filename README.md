# GestorSpa

Sistema de gestión para spa que permite administrar servicios, turnos y clientes.

## Requisitos Previos

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

### 🔑 Usuarios Demo Incluidos

| Usuario | Contraseña | Rol | Email |
|---------|------------|-----|-------|
| `cliente_demo` | `demo123` | Cliente | cliente@demo.com |
| `profesional_demo` | `demo123` | Profesional | profesional@demo.com |
| `admin_demo` | `demo123` | Administrador | admin@demo.com |

### 🛠️ Comandos de Gestión de Roles

```bash
# Configurar roles iniciales
python manage.py setup_roles --create-groups

# Listar roles disponibles
python manage.py setup_roles --list-roles

# Asignar rol a usuario
python manage.py setup_roles --assign-role username:cliente

# Ver roles de usuarios
python manage.py setup_roles --show-user-roles

# Crear usuarios demo
python manage.py create_demo_users
```

## Acceso al Sistema

### Login Público
- **URL:** `http://127.0.0.1:8000/login`
- **Usuarios demo disponibles** (ver tabla arriba)

### Panel de Administración
- **URL:** `http://127.0.0.1:8000/admin`
- **Usuario:** `admin_demo` / `demo123`

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

## Funcionalidades Avanzadas (2025)

### 💳 Gestión de Pagos y Descuentos
- Selección de método de pago (efectivo, débito, crédito) al reservar turno.
- Descuento automático del 15% para pagos con débito si aplica.
- Cálculo automático del total a pagar y registro de estado de pago.

### ⏰ Lógica de Reservas Inteligente
- Solo permite reservar turnos con al menos 48 horas de anticipación.
- Validación de disponibilidad de profesional y duración del servicio.
- Formulario de reserva adaptado según el rol y la lógica de negocio.

### 📧 Comprobantes Profesionales por Email
- Envío automático de comprobante de reserva al cliente por email.
- Comprobante incluye datos de la empresa, contacto y detalles del turno.
- Configuración de email segura vía variables de entorno.

### 📊 Reportes y Exportación
- Vista de reportes de turnos y pagos accesible solo para administradores.
- Filtros por fecha, profesional y servicio.
- Totales por servicio y profesional, listado detallado de turnos y pagos.
- Exportación de reportes a PDF (WeasyPrint) y CSV.
- Acceso a reportes desde el menú de administración.

### 🧭 Navegación y Mensajes Claros
- Menús dinámicos según el rol del usuario.
- Mensajes de éxito y error claros en todas las operaciones.
- Interfaz intuitiva y moderna.

## Ejemplo de Uso de Reportes y Pagos

1. Ingresar como administrador y acceder a "Reportes" desde el menú.
2. Filtrar por fechas, profesional o servicio según necesidad.
3. Descargar el reporte en PDF o CSV para análisis o impresión.
4. Al reservar un turno, seleccionar el método de pago y verificar el descuento automático si corresponde.
5. El cliente recibirá un comprobante profesional por email tras la reserva.

## Despliegue en Producción

- Configura `DEBUG=False` en el archivo `.env`.
- Asegúrate de definir correctamente las variables de email y base de datos.
- Usa un servidor WSGI (como Gunicorn o uWSGI) y un servidor web (Nginx/Apache) para producción.
- Ejecuta migraciones y crea un superusuario para el entorno productivo.
- Protege el acceso al panel de administración y reportes.

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

