"""Utilities to build markdown reports for E2E runs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


@dataclass
class CaseResult:
    name: str
    status: str
    details: str = ""


def build_markdown_report(
    case_results: Iterable[CaseResult],
    output_dir: Path,
    filename_prefix: str = "report",
) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{filename_prefix}_{timestamp}.md"

    lines = [
        f"# Terranote E2E Report – {timestamp}",
        "",
        "| Caso | Estado | Detalles |",
        "| --- | --- | --- |",
    ]
    for result in case_results:
        details = result.details.replace("\n", "<br>")
        lines.append(f"| {result.name} | {result.status} | {details} |")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    (output_dir / "latest.md").write_text("\n".join(lines), encoding="utf-8")
    return output_path


def consolidate_reports(source_dir: Path, summary_path: Path) -> Path:
    source_dir.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[str] = []
    for report_file in sorted(source_dir.glob("*.md")):
        if report_file.name == summary_path.name or report_file.name == "latest.md":
            continue
        rows.append(f"- [{report_file.name}]({report_file})")

    content = "\n".join(
        [
            "# Resumen de pruebas WhatsApp",
            "",
            "Reportes disponibles:",
            "",
            *(rows or ["(Aún no se han ejecutado pruebas)"]),
        ]
    )
    summary_path.write_text(content, encoding="utf-8")
    return summary_path


