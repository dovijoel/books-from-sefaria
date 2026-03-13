import enum
import uuid
from datetime import datetime
from sqlalchemy import DateTime, Enum, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus), default=JobStatus.PENDING, index=True
    )
    config_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    config_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    cover_pdf_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    page_count: Mapped[int | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
