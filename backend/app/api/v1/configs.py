"""
Saved book-configuration CRUD endpoints.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.config import BookConfig
from app.schemas.config import (
    BookConfigCreate,
    BookConfigListItem,
    BookConfigResponse,
)

router = APIRouter(prefix="/configs", tags=["configs"])


_FORMAT_EXCLUDE = {"name", "description", "texts"}


def _to_response(cfg: BookConfig) -> BookConfigResponse:
    data = json.loads(cfg.settings_json)
    fmt = {k: v for k, v in data.items() if k not in _FORMAT_EXCLUDE}
    return BookConfigResponse(
        **data,
        id=cfg.id,
        format=fmt,
        created_at=cfg.created_at.isoformat(),
        updated_at=cfg.updated_at.isoformat(),
    )


@router.get("", response_model=list[BookConfigListItem])
def list_configs(db: Session = Depends(get_db)):
    configs = db.query(BookConfig).order_by(BookConfig.updated_at.desc()).all()
    return [
        BookConfigListItem(
            id=c.id,
            name=c.name,
            description=c.description,
            created_at=c.created_at.isoformat(),
            updated_at=c.updated_at.isoformat(),
        )
        for c in configs
    ]


@router.post("", status_code=201, response_model=BookConfigResponse)
def create_config(payload: BookConfigCreate, db: Session = Depends(get_db)):
    cfg = BookConfig(
        id=str(uuid.uuid4()),
        name=payload.name,
        description=payload.description,
        settings_json=json.dumps(payload.model_dump()),
    )
    db.add(cfg)
    db.commit()
    db.refresh(cfg)
    return _to_response(cfg)


@router.get("/{config_id}", response_model=BookConfigResponse)
def get_config(config_id: str, db: Session = Depends(get_db)):
    cfg = db.get(BookConfig, config_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="Config not found")
    return _to_response(cfg)


@router.put("/{config_id}", response_model=BookConfigResponse)
def update_config(config_id: str, payload: BookConfigCreate, db: Session = Depends(get_db)):
    cfg = db.get(BookConfig, config_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="Config not found")
    cfg.name = payload.name
    cfg.description = payload.description
    cfg.settings_json = json.dumps(payload.model_dump())
    db.commit()
    db.refresh(cfg)
    return _to_response(cfg)


@router.delete("/{config_id}", status_code=204)
def delete_config(config_id: str, db: Session = Depends(get_db)):
    cfg = db.get(BookConfig, config_id)
    if not cfg:
        raise HTTPException(status_code=404, detail="Config not found")
    db.delete(cfg)
    db.commit()
