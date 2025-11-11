"""
Caso End-to-End: texto + ubicación → creación de nota y callback.

Requiere que el stack de infraestructura esté levantado (ver `terranote-infra`
compose/whatsapp-e2e) y que el adaptador exponga el webhook público configurado
en WhatsApp Cloud API.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone

import httpx

CORE_BASE_URL = os.environ.get("CORE_BASE_URL", "http://localhost:8000")
ADAPTER_BASE_URL = os.environ.get("ADAPTER_BASE_URL", "http://localhost:8001")
FAKE_OSM_BASE_URL = os.environ.get("FAKE_OSM_BASE_URL", "http://localhost:8080")

TEST_USER_MSISDN = os.environ.get("TEST_USER_MSISDN", "573000000000")
TEST_MESSAGE = os.environ.get("TEST_MESSAGE", "Hay una vía cerrada por obras.")
TEST_LATITUDE = float(os.environ.get("TEST_LATITUDE", "4.711"))
TEST_LONGITUDE = float(os.environ.get("TEST_LONGITUDE", "-74.0721"))


def _send_to_adapter(payload: dict) -> dict:
    with httpx.Client(base_url=ADAPTER_BASE_URL, timeout=10.0) as client:
        response = client.post("/webhook", json=payload)
        response.raise_for_status()
        return response.json()


def _format_timestamp() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


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

    print("[1/3] Enviando texto...")
    text_response = _send_to_adapter(text_event)
    print("Respuesta:", text_response)

    print("[2/3] Enviando ubicación...")
    location_response = _send_to_adapter(location_event)
    print("Respuesta:", location_response)

    print(
        "[3/3] Verificar callback en logs del adaptador y nota creada en core/fake OSM.",
    )


if __name__ == "__main__":
    main()


