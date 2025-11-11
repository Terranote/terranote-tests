"""
Caso End-to-End: texto sin ubicación → expiración por falta de ubicación.
"""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import httpx

ADAPTER_BASE_URL = os.environ.get("ADAPTER_BASE_URL", "http://localhost:8001")
LOG_DIR = Path(os.environ.get("LOG_DIR", "./logs"))

TEST_USER_MSISDN = os.environ.get("TEST_USER_MSISDN", "573000000000")
TEST_MESSAGE = os.environ.get("TEST_MESSAGE", "Prueba sin ubicación.")

LOG_DIR.mkdir(parents=True, exist_ok=True)


def _send_to_adapter(payload: dict) -> dict:
    with httpx.Client(base_url=ADAPTER_BASE_URL, timeout=10.0) as client:
        response = client.post("/webhook", json=payload)
        response.raise_for_status()
        return response.json()


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
                                    "id": "wamid.text_missing_location",
                                    "timestamp": datetime.now(tz=timezone.utc).isoformat(),
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

    print("[1/2] Enviando texto sin ubicación...")
    response = _send_to_adapter(text_event)
    print("Respuesta:", response)

    log_content = f"Texto sin ubicación:\n{response}\n"
    timestamp = datetime.now().isoformat()
    (LOG_DIR / f"whatsapp_missing_location_{timestamp}.log").write_text(
        log_content,
        encoding="utf-8",
    )

    print(
        "[2/2] Esperar >20 segundos y verificar que el adaptador descarte la sesión. "
        "Revisar logs/respuestas del adaptador para confirmarlo.",
    )


if __name__ == "__main__":
    main()


