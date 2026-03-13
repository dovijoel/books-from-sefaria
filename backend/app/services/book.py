"""
Book-build orchestrator service.
"""
from __future__ import annotations

import os
import tempfile

import app.services.sefaria as sefaria_svc
from app.services import latex
from app.services.latex import compile_latex


async def build_book(config: dict, job_id: str) -> str:
    """
    Orchestrate the full build:
    1. Fetch text and commentary links from Sefaria for each text entry.
    2. Generate the LaTeX document.
    3. Compile to PDF.

    Returns the path to the compiled PDF.
    """
    augmented_texts = []
    for text_entry in config.get("texts", []):
        fetched = await sefaria_svc.pull_text(text_entry["link"])
        text_with_data = {**text_entry, **fetched}
        if text_entry.get("commentary"):
            links = await sefaria_svc.pull_links(text_entry["link"])
            text_with_data["links"] = links
        augmented_texts.append(text_with_data)

    augmented_config = {**config, "texts": augmented_texts}
    latex_source = latex.generate_latex(augmented_config)

    tmp_dir = tempfile.mkdtemp(prefix=f"sefaria-{job_id}-")
    tex_path = os.path.join(tmp_dir, f"{job_id}.tex")
    with open(tex_path, "w", encoding="utf-8") as fh:
        fh.write(latex_source)

    return compile_latex(tex_path, config.get("format") or {})
