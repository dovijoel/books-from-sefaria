"""
Book-build orchestrator service.
Called by the Celery task; updates job status in the DB.
"""
from __future__ import annotations

import json
import os
import tempfile
from typing import Any

from sqlalchemy.orm import Session

from app.config import settings
from app.models.job import Job, JobStatus
from app.schemas.config import BookConfigCreate, config_to_dict
from app.services.latex import compile_latex, make_cover, pullinput, writeoutput


def _job_dir(job_id: str) -> str:
    path = os.path.join(settings.pdf_output_dir, job_id)
    os.makedirs(path, exist_ok=True)
    return path


def build_book(config: BookConfigCreate, job_id: str, db: Session) -> str:
    """
    Orchestrate the full build:
    1. Load templates
    2. Call writeoutput → produce <job_id>.tex
    3. Compile with xelatex → <job_id>.pdf
    4. Build cover → compile → <job_id>_cover.pdf
    5. Persist results in DB

    Returns the path to the final (rotated) PDF.
    """
    job = db.get(Job, job_id)
    if job is None:
        raise ValueError(f"Job {job_id} not found")

    job.status = JobStatus.RUNNING
    db.commit()

    try:
        work_dir = _job_dir(job_id)
        output_tex = os.path.join(work_dir, f"{job_id}.tex")

        formatting = config_to_dict(config)
        formatting["name"] = config.name  # keep name in case latex funcs need it

        template = pullinput(os.path.join(settings.resources_dir, "input.tex"))
        cover_template = pullinput(os.path.join(settings.resources_dir, "input_cover.tex"))

        # Write main .tex and get cover title
        cover_title = writeoutput(
            outputpath=output_tex,
            template=template,
            formatting=formatting,
            links_dir=settings.links_dir,
            resources_dir=settings.resources_dir,
        )

        # Compile main document
        pages = compile_latex(output_tex, formatting)

        # Build cover
        cover_tex = output_tex.replace(".tex", "_cover.tex")
        make_cover(
            outputpath=cover_tex,
            cover_template=cover_template,
            title=cover_title,
            settings_dict=formatting,
            pages=pages,
            resources_dir=settings.resources_dir,
        )
        compile_latex(cover_tex, formatting)

        pdf_path = output_tex.replace(".tex", ".rotated.pdf")
        cover_pdf = cover_tex.replace(".tex", ".rotated.pdf")

        job.status = JobStatus.SUCCESS
        job.pdf_path = pdf_path
        job.cover_pdf_path = cover_pdf
        job.page_count = pages
        db.commit()
        return pdf_path

    except Exception as exc:
        job.status = JobStatus.FAILURE
        job.error_message = str(exc)
        db.commit()
        raise
