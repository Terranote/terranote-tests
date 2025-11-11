"""
Caso End-to-End: texto sin ubicación → expiración por falta de ubicación.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from tools.reporting import CaseResult, build_markdown_report

ADAPTER_BASE_URL = os.environ.get("ADAPTER_BASE_URL", "http://localhost:8001")
FAKE_OSM_BASE_URL = os.environ.get("FAKE_OSM_BASE_URL", "http://localhost:8080")
LOG_DIR = Path(os.environ.get("LOG_DIR", "./logs"))

TEST_USER_MSISDN = os.environ.get("TEST_USER_MSISDN", "573000000000")
TEST_MESSAGE = os.environ.get("TEST_MESSAGE", "Prueba sin ubicación.")

LOG_DIR.mkdir(parents=True, exist_ok=True)


def _send_to_adapter(payload: dict) -> dict:
    with httpx.Client(base_url=ADAPTER_BASE_URL, timeout=10.0) as client:
        response = client.post("/webhook", json=payload)
        response.raise_for_status()
        return response.json()


def _fetch_callback_events() -> list[dict[str, Any]]:
    with httpx.Client(base_url=FAKE_OSM_BASE_URL, timeout=10.0) as client:
        response = client.get("/__control__/events")
        response.raise_for_status()
        return response.json()


def main() -> None:
    baseline_events = len(_fetch_callback_events())
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

    print("[1/3] Enviando texto sin ubicación...")
    response = _send_to_adapter(text_event)
    print("Respuesta:", response)

    print("[2/3] Esperando 25 segundos para validar expiración...")
    time.sleep(25)

    events = _fetch_callback_events()
    created_events = [
        event for event in events if event.get("type") == "note-created"
    ]
    if len(events) > baseline_events:
        raise AssertionError(
            "Se registró una nota a pesar de faltar la ubicación. Eventos: "
            f"{created_events}",
        )

    log_content = f"Texto sin ubicación:\n{response}\nEventos:\n{events}\n"
    timestamp = datetime.now().isoformat()
    log_path = LOG_DIR / f"whatsapp_missing_location_{timestamp}.log"
    log_path.write_text(log_content, encoding="utf-8")

    report_path = build_markdown_report(
        [
            CaseResult(
                name="Expiración sin ubicación",
                status="OK",
                details=str(log_path),
            ),
        ],
        output_dir=Path("reports/whatsapp"),
        filename_prefix="whatsapp_missing_location",
    )

    print("✅ Caso sin ubicación verificado (no se creó nota).")
    print(f"📄 Registro: {log_path}")
    print(f"📝 Reporte: {report_path}")


if __name__ == "__main__":
    main()


