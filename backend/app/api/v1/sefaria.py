"""
Sefaria text-lookup endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from app.schemas.sefaria import NameSearchResult, TextInfo
from app.services import sefaria as sefaria_svc

router = APIRouter(prefix="/sefaria", tags=["sefaria"])


@router.get("/search", response_model=list[NameSearchResult])
async def search_sefaria(q: str = Query(..., min_length=2, description="Text search query")):
    """Search Sefaria for a text by name."""
    data = await sefaria_svc.search_names(q)
    completions = data.get("completions", [])
    results = []
    for item in completions[:20]:
        if isinstance(item, str):
            results.append(
                NameSearchResult(ref=item, title=item, heTitle="", type="ref")
            )
        elif isinstance(item, dict):
            results.append(
                NameSearchResult(
                    ref=item.get("key", ""),
                    title=item.get("title", ""),
                    heTitle=item.get("heTitle", ""),
                    type=item.get("type", "ref"),
                )
            )
    return results


@router.get("/text/{ref:path}", response_model=TextInfo)
async def get_text_info(ref: str):
    """Return metadata for a Sefaria text ref."""
    try:
        data = sefaria_svc.pull_text(ref)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return TextInfo(
        ref=data.get("ref", ref),
        heTitle=data.get("heTitle", ""),
        title=data.get("title", ref),
        categories=data.get("categories", []),
        sectionNames=data.get("sectionNames", []),
    )
