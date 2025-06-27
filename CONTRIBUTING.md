# Guía de Contribución - GestorSpa

¡Gracias por considerar contribuir a GestorSpa! Este documento te ayudará a empezar con el desarrollo.

## 🚀 Configuración del Entorno de Desarrollo

### Prerrequisitos
- Python 3.8 o superior
- PostgreSQL (opcional, también funciona con SQLite)
- Git

### Configuración Inicial

1. **Fork y clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/GestorSpa.git
cd GestorSpa
```

2. **Crear entorno virtual**
```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/Mac
python3 -m venv env
source env/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
# Copiar el archivo de ejemplo
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Ejecutar migraciones**
```bash
python manage.py migrate
```

6. **Crear superusuario**
```bash
python manage.py createsuperuser
```

7. **Configurar roles del sistema**
```bash
python manage.py setup_roles --create-groups
```

## 🔧 Estructura del Proyecto

```
GestorSpa/
├── apps/
│   ├── servicios/     # Gestión de servicios del spa
│   ├── turnos/        # Sistema de reservas y turnos
│   └── usuarios/      # Gestión de usuarios y roles
├── configuraciones/   # Settings de Django
├── templates/         # Templates HTML
├── static/           # Archivos estáticos (CSS, JS, imágenes)
└── media/            # Archivos subidos por usuarios
```

## 🎯 Tipos de Contribuciones

### 🐛 Reportar Bugs
- Usa el sistema de Issues de GitHub
- Incluye pasos para reproducir el error
- Especifica la versión de Python y Django

### ✨ Nuevas Funcionalidades
- Abre un Issue primero para discutir la funcionalidad
- Asegúrate de que esté alineada con los objetivos del proyecto
- Escribe tests para nueva funcionalidad

### 📚 Documentación
- Mejoras en README.md
- Comentarios en el código
- Documentación de APIs

## 🔄 Proceso de Desarrollo

### Workflow de Git
1. Crear una nueva rama desde `main`
```bash
git checkout -b feature/nueva-funcionalidad
```

2. Hacer commits con mensajes descriptivos
```bash
git commit -m "✨ Agregar funcionalidad X"
```

3. Push de la rama
```bash
git push origin feature/nueva-funcionalidad
```

4. Crear Pull Request en GitHub

### Convenciones de Commits
Usa emojis para categorizar commits:
- ✨ `:sparkles:` - Nueva funcionalidad
- 🐛 `:bug:` - Corrección de bug
- 📚 `:books:` - Documentación
- 🎨 `:art:` - Mejoras de UI/UX
- ♻️ `:recycle:` - Refactoring
- ⚡ `:zap:` - Mejoras de rendimiento
- 🧹 `:broom:` - Limpieza de código

## 🧪 Testing

```bash
# Ejecutar tests
python manage.py test

# Ejecutar tests con coverage
pip install coverage
coverage run manage.py test
coverage report
```

## 📋 Checklist para Pull Requests

- [ ] El código sigue las convenciones de Python (PEP 8)
- [ ] Los tests pasan correctamente
- [ ] Se agregaron tests para nueva funcionalidad
- [ ] La documentación está actualizada
- [ ] Los commits tienen mensajes descriptivos
- [ ] Se probó en entorno local

## 🎨 Estándares de Código

### Python
- Seguir PEP 8
- Usar nombres descriptivos para variables y funciones
- Comentar código complejo
- Mantener funciones pequeñas y enfocadas

### Django
- Usar Django Forms para validación
- Implementar permisos apropiados
- Usar templates heredados
- Seguir el patrón MVT (Model-View-Template)

### HTML/CSS
- Usar Bootstrap 5 para consistencia
- Templates responsivos
- Código accesible (ARIA labels, etc.)

## 🤝 Código de Conducta

- Sé respetuoso con otros contribuidores
- Mantén un ambiente positivo y colaborativo
- Acepta críticas constructivas
- Ayuda a nuevos contribuidores

## 📞 Contacto

Si tienes preguntas sobre el desarrollo:
- Abre un Issue en GitHub
- Contacta a los mantenedores del proyecto

¡Gracias por contribuir a GestorSpa! 🎉
