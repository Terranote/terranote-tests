"""
Caso End-to-End: solo texto (sin ubicación) → no se crea nota.

Verifica que cuando se envía solo texto sin ubicación, el sistema no crea
una nota y eventualmente notifica al usuario (en fases futuras).
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

# Allow running the script directly.
import sys

ROOT = Path(__file__).resolve().parents[4]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.reporting import CaseResult, build_markdown_report, consolidate_reports  # noqa: E402

CORE_BASE_URL = os.environ.get("CORE_BASE_URL", "http://localhost:8002")
ADAPTER_BASE_URL = os.environ.get("ADAPTER_BASE_URL", "http://localhost:3000")
FAKE_OSM_BASE_URL = os.environ.get("FAKE_OSM_BASE_URL", "http://localhost:8080")
LOG_DIR = Path(os.environ.get("LOG_DIR", "./logs"))

TEST_USER_ID = int(os.environ.get("TEST_USER_ID", "123456789"))
TEST_MESSAGE = os.environ.get("TEST_MESSAGE", "Hay una vía cerrada por obras.")

LOG_DIR.mkdir(parents=True, exist_ok=True)


def _send_to_adapter(payload: dict) -> dict:
    """Envía un webhook update de Telegram al adaptador."""
    with httpx.Client(base_url=ADAPTER_BASE_URL, timeout=10.0) as client:
        response = client.post("/telegram/webhook", json=payload)
        response.raise_for_status()
        return response.json()


def _format_timestamp() -> int:
    """Retorna el timestamp de Unix en segundos."""
    return int(datetime.now(tz=timezone.utc).timestamp())


def _fetch_callback_events() -> list[dict[str, Any]]:
    """Recupera eventos registrados en fake OSM (simula callback)."""
    with httpx.Client(base_url=FAKE_OSM_BASE_URL, timeout=10.0) as client:
        response = client.get("/__control__/events")
        response.raise_for_status()
        return response.json()


def _fetch_latest_note() -> dict[str, Any] | None:
    """Obtiene la última nota creada en fake OSM, o None si no hay notas."""
    with httpx.Client(base_url=FAKE_OSM_BASE_URL, timeout=10.0) as client:
        response = client.get("/api/0.6/notes.json")
        response.raise_for_status()
        notes = response.json().get("features", [])
        return notes[-1] if notes else None


def _write_log(filename: str, content: str) -> Path:
    """Escribe un archivo de log."""
    output_path = LOG_DIR / filename
    output_path.write_text(content, encoding="utf-8")
    return output_path


def main() -> None:
    # Obtener estado inicial
    initial_events = _fetch_callback_events()
    baseline_event_count = len(initial_events)
    initial_note = _fetch_latest_note()
    initial_note_id = initial_note.get("properties", {}).get("id") if initial_note else None

    # Update con mensaje de texto (sin ubicación)
    text_update = {
        "update_id": 100000003,
        "message": {
            "message_id": 3,
            "date": _format_timestamp(),
            "from": {
                "id": TEST_USER_ID,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser"
            },
            "chat": {
                "id": TEST_USER_ID,
                "type": "private"
            },
            "text": TEST_MESSAGE
        }
    }

    print("[1/3] Enviando solo texto (sin ubicación)...")
    text_response = _send_to_adapter(text_update)
    print("Respuesta:", text_response)

    # Esperar más de 20 segundos para que expire la sesión
    print("[2/3] Esperando 25 segundos para que expire la sesión...")
    time.sleep(25)

    print("[3/3] Verificando que NO se creó nota...")
    final_events = _fetch_callback_events()
    final_note = _fetch_latest_note()
    final_note_id = final_note.get("properties", {}).get("id") if final_note else None

    # Verificar que no se creó nueva nota
    new_events = [e for e in final_events if e not in initial_events]
    note_created_events = [e for e in new_events if e.get("type") == "note-created"]

    if note_created_events:
        raise AssertionError(f"Se creó una nota cuando no debería: {note_created_events}")

    if final_note_id != initial_note_id:
        raise AssertionError(
            f"Se creó una nueva nota (ID: {final_note_id}) cuando no debería. "
            f"Nota inicial: {initial_note_id}"
        )

    log_content = (
        f"Texto enviado:\n{text_response}\n\n"
        f"Eventos iniciales: {baseline_event_count}\n"
        f"Eventos finales: {len(final_events)}\n"
        f"Nuevos eventos: {len(new_events)}\n"
        f"Eventos 'note-created': {len(note_created_events)}\n"
        f"Nota inicial ID: {initial_note_id}\n"
        f"Nota final ID: {final_note_id}\n"
    )
    timestamp = datetime.now().isoformat()
    log_path = _write_log(f"telegram_missing_location_{timestamp}.log", log_content)
    report_path = build_markdown_report(
        [CaseResult(name="Solo texto (sin ubicación)", status="OK", details=str(log_path))],
        output_dir=Path("reports/telegram"),
        filename_prefix="telegram_missing_location",
    )
    consolidate_reports(
        Path("reports/telegram"),
        Path("reports/telegram/summary.md"),
        title="Resumen de pruebas Telegram"
    )

    print("✅ Caso solo texto (sin ubicación) verificado correctamente.")
    print(f"📄 Registro almacenado en {log_path}")
    print(f"📝 Reporte: {report_path}")


if __name__ == "__main__":
    main()

