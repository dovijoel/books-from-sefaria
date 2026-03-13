"""
Book-build orchestrator service.
"""
from __future__ import annotations

import os

import app.services.sefaria as sefaria_svc
from app.services.sefaria import pull_text_sync
from app.config import settings
from app.services import latex
from app.services.latex import compile_latex, make_cover, pullinput


def build_book(config: dict, job_id: str) -> tuple[str, str | None, int]:
    """
    Orchestrate the full build:
    1. Fetch text from Sefaria for each text entry (sync).
    2. Generate the LaTeX document.
    3. Compile to PDF with xelatex.
    4. Optionally generate cover PDF.

    Returns (pdf_path, cover_pdf_path | None, page_count).
    """
    # Step 1: augment each text entry with live Sefaria data
    augmented_texts = []
    for text_entry in config.get("texts", []):
        if not isinstance(text_entry, dict):
            text_entry = text_entry.model_dump() if hasattr(text_entry, "model_dump") else dict(text_entry)
        # Strip None values from per-text format so global defaults fill in properly
        fmt = text_entry.get("format") or {}
        if isinstance(fmt, dict):
            fmt = {k: v for k, v in fmt.items() if v is not None}
        else:
            fmt = {}
        text_entry = {**text_entry, "format": fmt}
        fetched = pull_text_sync(text_entry["link"])
        augmented_texts.append({**text_entry, **fetched})

    # Step 2: generate LaTeX source
    augmented_config = {**config, "texts": augmented_texts}
    latex_source = latex.generate_latex(augmented_config)

    # Step 3: write .tex and compile
    output_dir = settings.pdf_output_dir
    os.makedirs(output_dir, exist_ok=True)
    tex_path = os.path.join(output_dir, f"{job_id}.tex")
    with open(tex_path, "w", encoding="utf-8") as fh:
        fh.write(latex_source)

    page_count = compile_latex(tex_path, config)
    pdf_path = tex_path.replace(".tex", ".pdf")
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"xelatex did not produce {pdf_path}")

    # Step 4: generate cover PDF (optional)
    cover_pdf_path: str | None = None
    resources_dir = settings.resources_dir
    cover_template_path = os.path.join(resources_dir, "input_cover.tex")
    if config.get("covertype") and os.path.isfile(cover_template_path):
        cover_template = pullinput(cover_template_path)
        title = config.get("titleheb") or config.get("title") or ""
        make_cover(tex_path, cover_template, title, config, page_count, resources_dir)
        cover_tex_path = tex_path.replace(".tex", "_cover.tex")
        if os.path.isfile(cover_tex_path):
            compile_latex(cover_tex_path, config)
            candidate = cover_tex_path.replace(".tex", ".pdf")
            if os.path.isfile(candidate):
                cover_pdf_path = candidate

    return pdf_path, cover_pdf_path, page_count
