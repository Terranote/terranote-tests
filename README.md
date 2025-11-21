# Terranote Tests

Suites de integración y end-to-end para el ecosistema Terranote.

## Objetivo

- Orquestar pruebas reales que verifiquen los flujos completos entre `terranote-core`, los adaptadores (WhatsApp, Telegram, etc.) y los servicios auxiliares (fake OSM, túneles, plataformas externas).
- Facilitar la ejecución reproducible de estos escenarios mediante scripts y configuraciones compartidas.
- Documentar los casos, datos de prueba y pasos manuales necesarios para validar nuevas versiones antes de su despliegue.

## Repositorios relacionados

- [`terranote-core`](https://github.com/Terranote/terranote-core)
- [`terranote-adapter-whatsapp`](https://github.com/Terranote/terranote-adapter-whatsapp)
- [`terranote-infra`](https://github.com/Terranote/terranote-infra) (compone el entorno Docker para pruebas E2E)

## Estructura

```
terranote-tests/
├── README.md
├── scenarios/
│   ├── whatsapp/
│   │   ├── cases/
│   │   └── env/
│   └── telegram/
│       ├── cases/
│       └── env/
└── tools/ (utilidades comunes)
```

- `scenarios/<canal>/cases`: scripts o suites que ejercen casos concretos (texto+ubicación, expiraciones, callback, etc.).
- `scenarios/<canal>/env`: ejemplos de variables de entorno y configuraciones para conectar con sandbox reales.
- `tools/`: utilidades compartidas (helpers HTTP, validadores de payloads, aserciones).

## Prerrequisitos

- Clonar los repositorios mencionados dentro del mismo directorio base (ver README de `terranote-infra`).
- Levantar el entorno con `docker compose` desde `terranote-infra/compose/<escenario>` (WhatsApp) o tener los servicios corriendo con systemd (Telegram).
- Contar con las credenciales/tokens necesarios:
  - WhatsApp Cloud API (para pruebas de WhatsApp)
  - Telegram Bot Token (obtenido de @BotFather, para pruebas de Telegram)

## Escenarios Disponibles

### WhatsApp

Suites de prueba para el adaptador de WhatsApp. Ver [`scenarios/whatsapp/cases/README.md`](scenarios/whatsapp/cases/README.md) para detalles.

Los resultados se generan en `reports/whatsapp/`, y el resumen consolidado en `reports/whatsapp/summary.md`.

### Telegram

Suites de prueba para el adaptador de Telegram. Ver [`scenarios/telegram/cases/README.md`](scenarios/telegram/cases/README.md) para detalles.

Los resultados se generan en `reports/telegram/`, y el resumen consolidado en `reports/telegram/summary.md`.

## Próximos pasos

1. ✅ Crear la primera suite para WhatsApp
2. ✅ Crear estructura de escenarios para Telegram
3. ⏳ Implementar casos de prueba para Telegram
4. Integrar las suites con CI (opcionalmente) o documentar cómo ejecutarlas manualmente antes de releases.

## Licencia

GPL-3.0-or-later.
