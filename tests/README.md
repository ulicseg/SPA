# Tests del Sistema GestorSpa

Este directorio contiene todos los scripts de prueba para verificar el correcto funcionamiento del sistema.

## Archivos de Prueba

### `test_encoding_fix.py`
- **Propósito**: Verificar que el sistema maneja correctamente caracteres especiales UTF-8
- **Resultado**: ✅ EXITOSO - No hay errores de encoding
- **Uso**: `python tests/test_encoding_fix.py`

### `test_email_system.py`
- **Propósito**: Probar el envío de emails con caracteres especiales
- **Resultado**: ✅ EXITOSO - Emails se procesan sin errores
- **Uso**: `python tests/test_email_system.py`

### `test_reservation_system.py`
- **Propósito**: Prueba completa del flujo de reservas
- **Resultado**: ✅ EXITOSO - Sistema funciona correctamente
- **Uso**: `python tests/test_reservation_system.py`

## Estado de las Pruebas

🎉 **TODAS LAS PRUEBAS EXITOSAS** - El problema de encoding UTF-8 ha sido completamente resuelto.

## Ejecutar Todas las Pruebas

```bash
# Ejecutar pruebas individuales
python tests/test_encoding_fix.py
python tests/test_email_system.py
python tests/test_reservation_system.py
```

## Notas

- Todas las pruebas verifican que el sistema maneja correctamente caracteres especiales del español
- Los tests incluyen nombres con ñ, acentos y otros caracteres UTF-8
- El sistema ahora es robusto contra errores de encoding
