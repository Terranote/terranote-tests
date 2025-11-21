# Casos de prueba – Telegram

## Caso 1: Texto + Ubicación (creación de nota)

- Enviar un mensaje de texto seguido de la ubicación actual dentro de una ventana < 20 segundos.
- Verificar:
  - Respuesta del adaptador (`status=accepted` / `processed=1`).
  - Callback recibido por el adaptador (`note-created`) con la URL de la nota.
  - Contenido de la nota en OSM (fake o real) con texto y coordenadas correctas.

Script sugerido: `scripts/test_text_location.py`

## Caso 2: Solo Texto (sin ubicación)

- Enviar solo texto y no enviar ubicación.
- Esperar > 20 segundos y comprobar que el adaptador notifica al usuario que se requiere la ubicación.
- Verificar que no se crea nota.
- Script sugerido: `scripts/test_missing_location.py`

## Caso 3: Solo Ubicación (sin texto)

- Enviar únicamente la ubicación y no añadir texto.
- Esperar > 20 segundos y revisar la respuesta del adaptador (mensaje al usuario indicando que falta texto).
- Confirmar que no se crea nota.
- Script sugerido: `scripts/test_missing_text.py`

## Caso 4: Reintento con nueva sesión

- Repetir caso 1 inmediatamente después de cerrar la sesión para validar que una segunda nota se crea correctamente con una nueva ventana de interacción.

## Estructura de Payloads de Telegram

Los webhooks de Telegram tienen el siguiente formato:

```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": {
      "id": 123456789,
      "is_bot": false,
      "first_name": "Test",
      "username": "testuser"
    },
    "chat": {
      "id": 123456789,
      "type": "private"
    },
    "date": 1234567890,
    "text": "Mensaje de prueba"
  }
}
```

Para ubicación:

```json
{
  "update_id": 123456790,
  "message": {
    "message_id": 2,
    "from": {
      "id": 123456789,
      "is_bot": false,
      "first_name": "Test",
      "username": "testuser"
    },
    "chat": {
      "id": 123456789,
      "type": "private"
    },
    "date": 1234567891,
    "location": {
      "latitude": 4.711,
      "longitude": -74.0721
    }
  }
}
```

Cada caso puede convertirse en un script automatizado (por ejemplo, usando `pytest` o scripts Python) que:

1. Simula el webhook de Telegram enviando payloads al adaptador.
2. Consulta el estado del núcleo/fake OSM para validar resultados.
3. Registra en un reporte los pasos y resultados obtenidos.

