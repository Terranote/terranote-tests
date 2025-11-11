"""
Caso End-to-End: texto + ubicación → creación de nota y callback.

Requiere que el stack de infraestructura esté levantado (ver `terranote-infra`
compose/whatsapp-e2e) y que el adaptador exponga el webhook público configurado
en WhatsApp Cloud API.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx

CORE_BASE_URL = os.environ.get("CORE_BASE_URL", "http://localhost:8000")
ADAPTER_BASE_URL = os.environ.get("ADAPTER_BASE_URL", "http://localhost:8001")
FAKE_OSM_BASE_URL = os.environ.get("FAKE_OSM_BASE_URL", "http://localhost:8080")
LOG_DIR = Path(os.environ.get("LOG_DIR", "./logs"))

TEST_USER_MSISDN = os.environ.get("TEST_USER_MSISDN", "573000000000")
TEST_MESSAGE = os.environ.get("TEST_MESSAGE", "Hay una vía cerrada por obras.")
TEST_LATITUDE = float(os.environ.get("TEST_LATITUDE", "4.711"))
TEST_LONGITUDE = float(os.environ.get("TEST_LONGITUDE", "-74.0721"))

LOG_DIR.mkdir(parents=True, exist_ok=True)


def _send_to_adapter(payload: dict) -> dict:
    with httpx.Client(base_url=ADAPTER_BASE_URL, timeout=10.0) as client:
        response = client.post("/webhook", json=payload)
        response.raise_for_status()
        return response.json()


def _format_timestamp() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _fetch_callback_events() -> list[dict[str, Any]]:
    """Recupera eventos registrados en fake OSM (simula callback)."""
    with httpx.Client(base_url=FAKE_OSM_BASE_URL, timeout=10.0) as client:
        response = client.get("/__control__/events")
        response.raise_for_status()
        return response.json()


def _fetch_latest_note() -> dict[str, Any]:
    with httpx.Client(base_url=FAKE_OSM_BASE_URL, timeout=10.0) as client:
        response = client.get("/api/0.6/notes.json")
        response.raise_for_status()
        notes = response.json().get("features", [])
        if not notes:
            raise RuntimeError("No se encontraron notas en fake OSM")
        return notes[-1]


def _write_log(filename: str, content: str) -> None:
    (LOG_DIR / filename).write_text(content, encoding="utf-8")


def main() -> None:
    text_event = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "wa_e2e",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "1555000000",
                                "phone_number_id": "phone-test",
                            },
                            "contacts": [],
                            "messages": [
                                {
                                    "from": TEST_USER_MSISDN,
                                    "id": "wamid.text",
                                    "timestamp": _format_timestamp(),
                                    "type": "text",
                                    "text": {"body": TEST_MESSAGE},
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }

    location_event = {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "wa_e2e",
                "changes": [
                    {
                        "field": "messages",
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "1555000000",
                                "phone_number_id": "phone-test",
                            },
                            "contacts": [],
                            "messages": [
                                {
                                    "from": TEST_USER_MSISDN,
                                    "id": "wamid.location",
                                    "timestamp": _format_timestamp(),
                                    "type": "location",
                                    "location": {
                                        "latitude": TEST_LATITUDE,
                                        "longitude": TEST_LONGITUDE,
                                    },
                                }
                            ],
                        },
                    }
                ],
            }
        ],
    }

    print("[1/4] Enviando texto...")
    text_response = _send_to_adapter(text_event)
    print("Respuesta:", text_response)

    print("[2/4] Enviando ubicación...")
    location_response = _send_to_adapter(location_event)
    print("Respuesta:", location_response)

    print("[3/4] Consultando eventos de callback en fake OSM...")
    events = _fetch_callback_events()
    callback = next(
        (event for event in events if event.get("type") == "note-created"),
        None,
    )
    if not callback:
        raise RuntimeError("No se encontró evento de callback 'note-created'")

    note_id = callback.get("payload", {}).get("note_id")
    print("Callback OK. note_id:", note_id)

    print("[4/4] Verificando última nota en fake OSM...")
    latest_note = _fetch_latest_note()
    geometry = latest_note.get("geometry", {}).get("coordinates", [])
    properties = latest_note.get("properties", {})
    text = properties.get("comments", [{}])[-1].get("text", "")

    if not (
        len(geometry) == 2
        and abs(float(geometry[0]) - TEST_LONGITUDE) < 1e-6
        and abs(float(geometry[1]) - TEST_LATITUDE) < 1e-6
    ):
        raise AssertionError(f"Coordenadas inesperadas: {geometry}")
    if TEST_MESSAGE not in text:
        raise AssertionError("El texto de la nota no coincide con el mensaje enviado")

    log_content = (
        f"Texto:\n{text_response}\n\n"
        f"Ubicación:\n{location_response}\n\n"
        f"Callback:\n{callback}\n\n"
        f"Nota:\n{latest_note}\n"
    )
    timestamp = datetime.now().isoformat()
    _write_log(f"whatsapp_text_location_{timestamp}.log", log_content)

    print("✅ Caso texto + ubicación verificado correctamente.")
    print(f"📄 Registro almacenado en {LOG_DIR}")


if __name__ == "__main__":
    main()


