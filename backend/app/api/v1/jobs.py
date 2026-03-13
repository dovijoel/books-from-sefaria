"""
Job management endpoints.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job import Job, JobStatus
from app.schemas.config import BookConfigCreate
from app.schemas.job import JobResponse
from app.workers.tasks import generate_pdf_task

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _job_response(job: Job) -> JobResponse:
    return JobResponse(
        id=job.id,
        status=job.status,
        config_id=job.config_id,
        pdf_path=job.pdf_path,
        cover_pdf_path=job.cover_pdf_path,
        error_message=job.error_message,
        page_count=job.page_count,
        created_at=job.created_at.isoformat(),
        updated_at=job.updated_at.isoformat(),
    )


@router.post("", status_code=202, response_model=JobResponse)
def create_job(config: BookConfigCreate, db: Session = Depends(get_db)):
    """Submit a new PDF-generation job."""
    job_id = str(uuid.uuid4())
    job = Job(
        id=job_id,
        status=JobStatus.PENDING,
        config_snapshot=json.dumps(config.model_dump()),
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    generate_pdf_task.apply_async(
        args=[config.model_dump(), job_id],
        task_id=job_id,
    )
    return _job_response(job)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_response(job)


@router.get("/{job_id}/download")
def download_pdf(job_id: str, kind: str = "pdf", db: Session = Depends(get_db)):
    """Download the generated PDF or cover PDF."""
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.SUCCESS:
        raise HTTPException(status_code=409, detail="Job is not complete")

    import os

    if kind == "cover":
        path = job.cover_pdf_path
    else:
        path = job.pdf_path

    if not path or not os.path.isfile(path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")

    filename = f"{job_id}_cover.pdf" if kind == "cover" else f"{job_id}.pdf"
    return FileResponse(path, media_type="application/pdf", filename=filename)
