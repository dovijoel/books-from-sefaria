"""
Book-build orchestrator service (synchronous – safe to call from Celery).
"""
from __future__ import annotations

import os
from typing import Any

import app.services.sefaria as sefaria_svc
from app.services import latex as latex_svc
from app.services.latex import compile_latex


def _to_dict(obj: Any) -> dict:
    """Convert a Pydantic model or dict-like object to a plain dict."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    return dict(obj)


def build_book(config: dict, job_id: str) -> tuple[str, int]:
    """
    Orchestrate a full PDF build:
    1. Fetch Hebrew (and optionally English) text from Sefaria-Export for each entry.
    2. Generate a .tex document.
    3. Compile to PDF with xelatex.

    Returns (pdf_path, page_count).
    """
    augmented_texts: list[dict] = []
    for raw_entry in config.get("texts", []):
        entry = _to_dict(raw_entry)

        # Fetch main (Hebrew) text.
        # GitHub-export JSONs use "text" for Hebrew; the live Sefaria API uses "he"
        # (which _normalize_live_api_response maps to "text"), so either way "text"
        # holds Hebrew after normalisation.  Keep "he" as a secondary fallback for
        # any responses that bypass normalisation.
        he_data = sefaria_svc.pull_text_sync(entry["link"])
        he_verses: list = he_data.get("text") or he_data.get("he") or []
        he_title: str = he_data.get("heTitle") or entry["link"]

        # English translation always comes from a separate file.
        en_verses: list = []
        translation_path: str = entry.get("translation") or ""
        if translation_path:
            en_data = sefaria_svc.pull_text_sync(translation_path)
            en_verses = en_data.get("text") or []

        # Normalise per-entry format overrides: drop None values
        fmt = entry.get("format") or {}
        if hasattr(fmt, "model_dump"):
            fmt = fmt.model_dump()
        clean_fmt = {k: v for k, v in fmt.items() if v is not None}

        augmented_entry = {
            **entry,
            "he": he_verses,
            "text": en_verses,
            "heTitle": he_title,
            "format": clean_fmt,
        }
        augmented_texts.append(augmented_entry)

    augmented_config = {**config, "texts": augmented_texts}

    # Write .tex to a shared directory accessible by both worker and backend containers.
    out_dir = os.environ.get("PDF_OUTPUT_DIR", "/tmp/pdf_output")
    os.makedirs(out_dir, exist_ok=True)
    tex_path = os.path.join(out_dir, f"{job_id}.tex")

    latex_source = latex_svc.generate_latex(augmented_config)
    with open(tex_path, "w", encoding="utf-8") as fh:
        fh.write(latex_source)

    # compile_latex(path, settings_dict) → int (page count)
    # The PDF is written next to the .tex file with a .pdf extension.
    page_count: int = compile_latex(tex_path, augmented_config)
    pdf_path = tex_path.replace(".tex", ".pdf")

    return pdf_path, page_count
