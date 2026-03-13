from __future__ import annotations

from app.database import SessionLocal
from app.schemas.config import BookConfigCreate
from app.services.book import build_book
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="tasks.generate_pdf", max_retries=2, default_retry_delay=30)
def generate_pdf_task(self, config_dict: dict, job_id: str) -> dict:
    """
    Celery task: deserialise config, run build_book, return result summary.
    """
    db = SessionLocal()
    try:
        config = BookConfigCreate(**config_dict)
        pdf_path = build_book(config, job_id, db)
        return {"job_id": job_id, "pdf_path": pdf_path}
    except Exception as exc:
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            return {"job_id": job_id, "error": str(exc)}
    finally:
        db.close()
