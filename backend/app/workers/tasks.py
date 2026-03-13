from __future__ import annotations

from app.database import SessionLocal
from app.models.job import Job, JobStatus
from app.schemas.config import BookConfigCreate, config_to_dict
from app.services.book import build_book
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="tasks.generate_pdf", max_retries=2, default_retry_delay=30)
def generate_pdf_task(self, config_dict: dict, job_id: str) -> dict:
    """
    Celery task: deserialise config, run build_book, update job record.
    """
    db = SessionLocal()
    try:
        # Mark job as running
        job = db.get(Job, job_id)
        if job:
            job.status = JobStatus.RUNNING
            db.commit()

        config = BookConfigCreate(**config_dict)
        flat_config = config_to_dict(config)
        pdf_path, page_count = build_book(flat_config, job_id)

        # Mark job as successful
        job = db.get(Job, job_id)
        if job:
            job.status = JobStatus.SUCCESS
            job.pdf_path = pdf_path
            job.page_count = page_count
            db.commit()

        return {"job_id": job_id, "pdf_path": pdf_path, "page_count": page_count}

    except Exception as exc:
        try:
            job = db.get(Job, job_id)
            if job:
                job.status = JobStatus.FAILURE
                job.error_message = str(exc)
                db.commit()
        except Exception:
            pass
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            return {"job_id": job_id, "error": str(exc)}
    finally:
        db.close()
