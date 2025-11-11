"""Genera un resumen consolidado de reportes E2E de WhatsApp."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.reporting import consolidate_reports


def main() -> None:
    reports_dir = Path("reports/whatsapp")
    summary_path = reports_dir / "summary.md"
    result = consolidate_reports(reports_dir, summary_path)
    print(f"Resumen actualizado en {result}")


if __name__ == "__main__":
    main()


