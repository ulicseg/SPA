# Documentación - GestorSpa

## Índice

1. [Guía de Usuario](user-guide.md)
2. [Guía de Administrador](admin-guide.md)
3. [API Documentation](api-docs.md)
4. [Configuración Avanzada](advanced-config.md)

## Arquitectura del Sistema

### Modelos de Datos

#### Usuario
- Sistema unificado de usuarios con perfiles específicos
- Roles: Cliente, Profesional, Administrador

#### Servicios
- Catálogo de servicios del spa
- Precios, duración, descripción
- Imágenes y categorías

#### Turnos
- Sistema de reservas
- Estados: Pendiente, Confirmado, Completado, Cancelado
- Notificaciones automáticas

### Flujo de Trabajo

1. **Cliente se registra** → Perfil automático con rol cliente
2. **Cliente selecciona servicio** → Ve profesionales disponibles
3. **Cliente elige fecha/hora** → Sistema valida disponibilidad
4. **Cliente confirma reserva** → Se envía notificación por email
5. **Profesional recibe notificación** → Puede gestionar desde su panel
6. **Administrador supervisa** → Panel completo de gestión

## Screenshots

Para agregar screenshots al README:
1. Toma capturas de pantalla del sistema
2. Guárdalas en `docs/images/`
3. Actualiza las referencias en README.md
