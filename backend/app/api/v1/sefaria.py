"""
Sefaria text-lookup endpoints.
"""
from __future__ import annotations

import httpx
from fastapi import APIRouter, HTTPException, Query
from app.schemas.sefaria import (
    CommentaryOption,
    NameSearchResult,
    TextResolveResult,
    TextVersion,
)
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


@router.get("/resolve/{ref:path}", response_model=TextResolveResult)
async def resolve_sefaria_ref(ref: str):
    """
    Resolve a canonical Sefaria ref (e.g. 'Esther') and return metadata for job creation.
    The 'link' field in the response is the value to use for texts[].link in job creation.
    """
    try:
        data = await sefaria_svc.pull_text(ref)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code if exc.response else 502
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return TextResolveResult(
        ref=ref,
        link=ref,  # The same ref works for the live API fallback
        heTitle=data.get("heTitle") or ref,
        title=data.get("title") or ref,
    )


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


@router.get("/versions/{ref:path}", response_model=list[TextVersion])
async def get_text_versions(ref: str):
    """Return available text versions/translations for a Sefaria text ref."""
    try:
        versions = await sefaria_svc.get_versions(ref)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code if exc.response else 502
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return [TextVersion(**v) for v in versions]


@router.get("/commentaries/{ref:path}", response_model=list[CommentaryOption])
async def get_text_commentaries(ref: str):
    """Return available commentaries for a Sefaria text ref."""
    try:
        commentaries = await sefaria_svc.get_commentaries(ref)
    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code if exc.response else 502
        raise HTTPException(status_code=status, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return [CommentaryOption(**c) for c in commentaries]
