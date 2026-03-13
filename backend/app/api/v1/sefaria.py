"""
Sefaria text-lookup endpoints.
"""
from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException, Query
from app.schemas.sefaria import NameSearchResult
from app.services import sefaria as sefaria_svc

router = APIRouter(prefix="/sefaria", tags=["sefaria"])


@router.get("/search", response_model=list[NameSearchResult])
async def search_sefaria(q: str = Query(..., min_length=2, description="Text search query")):
    """Search Sefaria for a text by name."""
    try:
        results = await sefaria_svc.search_texts(q)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return [
        NameSearchResult(
            ref=item.get("ref", ""),
            title=item.get("title", ""),
            heTitle=item.get("heTitle", ""),
            type=item.get("type", "ref"),
        )
        for item in results
    ]


@router.get("/text/{ref:path}")
async def get_text_info(ref: str):
    """Return full text data for a Sefaria text ref."""
    try:
        data = await sefaria_svc.pull_text(ref)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code if exc.response else 502
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return data


@router.get("/links/{ref:path}")
async def get_sefaria_links(ref: str, link_type: str | None = Query(default=None)):
    """Return links for a Sefaria text ref."""
    try:
        links = await sefaria_svc.pull_links(ref, link_type=link_type)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code if exc.response else 502
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return links
