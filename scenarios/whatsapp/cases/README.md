# Casos de prueba – WhatsApp

## Caso 1: Texto + Ubicación (creación de nota)

- Enviar un mensaje de texto seguido de la ubicación actual dentro de una ventana < 20 segundos.
- Verificar:
  - Respuesta del adaptador (`status=accepted` / `processed=1`).
  - Callback recibido por el adaptador (`note-created`) con la URL de la nota.
  - Contenido de la nota en OSM (fake o real) con texto y coordenadas correctas.

Script sugerido: `scripts/test_text_location.py`

## Caso 2: Expiración por falta de ubicación

- Enviar solo texto y no enviar ubicación.
- Esperar > 20 segundos y comprobar que el adaptador notifica al usuario que se requiere la ubicación (en fases siguientes).
- Verificar que no se crea nota.

## Caso 3: Expiración por falta de texto

- Enviar únicamente la ubicación y no añadir texto.
- Esperar > 20 segundos y revisar la respuesta del adaptador (mensaje al usuario indicando que falta texto).
- Confirmar que no se crea nota.

## Caso 4: Reintento con nueva sesión

- Repetir caso 1 inmediatamente después de cerrar la sesión para validar que una segunda nota se crea correctamente con una nueva ventana de interacción.

Cada caso puede convertirse en un script automatizado (por ejemplo, usando `pytest` o scripts shell) que:

1. Llama a la API de Meta (o al adaptador) con datos preparados.
2. Consulta el estado del núcleo/fake OSM para validar resultados.
3. Registra en un reporte los pasos y resultados obtenidos.


