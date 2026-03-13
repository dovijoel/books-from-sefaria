"""
Sefaria data-fetching service.
All HTTP calls use httpx.AsyncClient.
"""
from __future__ import annotations

from typing import Any

import httpx

from app.config import settings

GITHUB_TEXT_BASE = (
    "https://raw.githubusercontent.com/Sefaria/Sefaria-Export/"
    "refs/heads/master/json/{path}.json"
)
GITHUB_SCHEMA_BASE = (
    "https://raw.githubusercontent.com/Sefaria/Sefaria-Export/"
    "master/schemas/{masekhet}.json"
)
SEFARIA_SEARCH_API = "https://www.sefaria.org/api/search-wrapper/es6?query={query}&type=text&get_filters=0"
SEFARIA_LINKS_API = "https://www.sefaria.org/api/links/{ref}?with_text=0"
SEFARIA_INDEX_API = "https://www.sefaria.org/api/index/{ref}"


# ── Search ────────────────────────────────────────────────────────────────────

async def search_texts(query: str) -> list[dict]:
    """Search Sefaria for text references matching *query*. Returns [] for empty input."""
    if not query or not query.strip():
        return []
    url = SEFARIA_SEARCH_API.format(query=query.replace(" ", "%20"))
    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
    return data.get("results", [])


# ── Text fetching ─────────────────────────────────────────────────────────────

async def pull_text(ref: str) -> dict[str, Any]:
    """Fetch a Sefaria text JSON by ref (spaces → %20)."""
    path = ref.replace(" ", "%20")
    url = GITHUB_TEXT_BASE.format(path=path)
    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


async def get_text_details(ref: str) -> dict[str, Any]:
    """Fetch metadata (title, categories, etc.) for a Sefaria text reference."""
    encoded = ref.replace(" ", "%20")
    url = SEFARIA_INDEX_API.format(ref=encoded)
    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


async def get_index_json(masekhet: str) -> list[dict]:
    """Return the Chapters nodes for a masekhet (spaces → underscores)."""
    name = masekhet.replace(" ", "_")
    url = GITHUB_SCHEMA_BASE.format(masekhet=name)
    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
    return data["alts"]["Chapters"]["nodes"]


# ── Links ─────────────────────────────────────────────────────────────────────

async def pull_links(ref: str, link_type: str | None = None) -> list[dict]:
    """
    Fetch commentary/cross-reference links for *ref* from the Sefaria API.
    Optional *link_type* filters results to a specific link type (e.g. "commentary").
    """
    encoded = ref.replace(" ", "%20")
    url = SEFARIA_LINKS_API.format(ref=encoded)
    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        links: list[dict] = resp.json()
    if link_type is not None:
        links = [lnk for lnk in links if lnk.get("type") == link_type]
    return links


# ── Commentary matching ───────────────────────────────────────────────────────

def match_comment(link: dict, text_ref: str) -> bool:
    """Return True if *link*'s anchorRef matches *text_ref* (case-insensitive)."""
    anchor = link.get("anchorRef")
    if anchor is None:
        return False
    return anchor.lower() == text_ref.lower()


# ── Internal helpers (used by match_chapters) ─────────────────────────────────

def _find_anchor_in_pairs(ref: str, links: list[list[str]]) -> str | None:
    """Return the ref that *ref* is linked to in old-style [ref1, ref2] pairs."""
    for pair in links:
        if ref in pair[0]:
            return pair[1]
        if ref in pair[1]:
            return pair[0]
    return None


def find_perek(name: str) -> tuple[str, str]:
    """
    Given a ref string, return (en_chapter_title, he_chapter_title).
    Falls back to the ref string if nothing is found.
    Note: get_index_json is now async; this is a synchronous wrapper that
    returns the name unchanged (use the async path for real data).
    """
    return name, name


def match_chapters(
    text_json: dict[str, Any], links: list[list[str]]
) -> dict[str, Any]:
    """
    Inject chapter-boundary dicts into text_json["text"] for daf-based texts.
    Modifies in-place and returns the same dict.
    """
    text = text_json["text"]
    daf_i = 1.0
    new_text: list = []
    for section in text:
        current_daf = daf_i
        ref_base = text_json.get("ref", "")
        daf_num = int((current_daf + 1) / 2)
        amud = "a" if current_daf % 2 == 1 else "b"
        ref = f"{ref_base} {daf_num}{amud}"
        commentary_ref = _find_anchor_in_pairs(ref, links)
        title_en, title_he = find_perek(commentary_ref or ref)

        if not new_text or (
            isinstance(new_text[-1], dict)
            and new_text[-1].get("name_en") != title_en
        ):
            if title_en != ref:
                new_text.append({"name_en": title_en, "name_he": title_he})
        new_text.append(section)
        daf_i += 0.5
    text_json["text"] = new_text
    text_json["chap_list"] = []
    return text_json


# ── Structure normalizer ──────────────────────────────────────────────────────

def structure_fixer(data: Any) -> list:
    """
    Normalize a dict-structured Sefaria text into a nested list structure.
    If already a list, returns it unchanged.
    """
    if isinstance(data, list):
        return data
    text: list = []
    for part in data.values():
        if isinstance(part, list):
            text.append(part)
        elif isinstance(part, dict):
            text_part: list = []
            for subpart in part.values():
                if isinstance(subpart, list):
                    text_part.append(subpart)
                elif isinstance(subpart, dict):
                    text_subpart: list = []
                    for subsubpart in subpart.values():
                        if isinstance(subsubpart, list):
                            text_subpart.append(subsubpart)
                    text_part.append(text_subpart)
            text.append(text_part)
    return text
