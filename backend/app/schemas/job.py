from __future__ import annotations
from typing import Optional
from pydantic import BaseModel
from app.models.job import JobStatus


class JobResponse(BaseModel):
    id: str
    status: JobStatus
    config_id: Optional[str]
    pdf_path: Optional[str]
    cover_pdf_path: Optional[str]
    error_message: Optional[str]
    page_count: Optional[int]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}
