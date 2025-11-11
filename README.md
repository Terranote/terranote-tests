# Terranote Tests

Suites de integración y end-to-end para el ecosistema Terranote.

## Objetivo

- Orquestar pruebas reales que verifiquen los flujos completos entre `terranote-core`, los adaptadores (WhatsApp, Telegram, etc.) y los servicios auxiliares (fake OSM, túneles, plataformas externas).
- Facilitar la ejecución reproducible de estos escenarios mediante scripts y configuraciones compartidas.
- Documentar los casos, datos de prueba y pasos manuales necesarios para validar nuevas versiones antes de su despliegue.

## Repositorios relacionados

- [`terrnote-core`](https://github.com/Terranote/terranote-core)
- [`terranote-adapter-whatsapp`](https://github.com/Terranote/terranote-adapter-whatsapp)
- [`terranote-infra`](https://github.com/Terranote/terranote-infra) (compone el entorno Docker para pruebas E2E)

## Estructura propuesta

```
terranote-tests/
├── README.md
├── scenarios/
│   ├── whatsapp/
│   │   ├── cases/
│   │   └── env/
│   └── telegram/ (futuro)
└── tools/ (utilidades comunes)
```

- `scenarios/<canal>/cases`: scripts o suites que ejercen casos concretos (texto+ubicación, expiraciones, callback, etc.).
- `scenarios/<canal>/env`: ejemplos de variables de entorno y configuraciones para conectar con sandbox reales.
- `tools/`: utilidades compartidas (helpers HTTP, validadores de payloads, aserciones).

## Prerrequisitos

- Clonar los repositorios mencionados dentro del mismo directorio base (ver README de `terranote-infra`).
- Levantar el entorno con `docker compose` desde `terranote-infra/compose/<escenario>`.
- Contar con las credenciales/tokens necesarios de WhatsApp Cloud API (o el canal que se esté probando).

## Próximos pasos

1. Crear la primera suite para WhatsApp que cubra:
   - Mensaje de texto + ubicación → creación de nota → callback exitoso.
   - Sesión que expira (falta de ubicación o texto) → mensajes al usuario.
2. Añadir reportes (por ejemplo, salida en Markdown/HTML) para documentar los resultados.
3. Integrar las suites con CI (opcionalmente) o documentar cómo ejecutarlas manualmente antes de releases.

Los resultados individuales se generan en `reports/whatsapp/`, y el resumen consolidado en `reports/whatsapp/summary.md`.

## Licencia

GPL-3.0-or-later.
