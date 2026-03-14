"""
Sefaria data-fetching service.
All HTTP calls use httpx.AsyncClient.
"""
from __future__ import annotations

import html as html_lib
import re
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
SEFARIA_NAME_API = "https://www.sefaria.org/api/name/{query}?limit=20&type=ref"
SEFARIA_TEXT_API = "https://www.sefaria.org/api/texts/{ref}?context=0&pad=0&commentary=0"


# ── Search ────────────────────────────────────────────────────────────────────

async def search_texts(query: str) -> list[dict]:
    """
    Search Sefaria for text references matching *query* using the name-completion API.
    Returns book-level canonical refs (e.g. 'Esther', not 'Esther 1:1').
    Returns [] for empty input.
    """
    if not query or not query.strip():
        return []
    encoded = query.replace(" ", "%20")
    url = SEFARIA_NAME_API.format(query=encoded)
    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        data = resp.json()
    # Sefaria API v2+ returns "completion_objects"; older versions used "matches"
    matches: list[dict] = data.get("completion_objects", data.get("matches", []))
    # Keep only top-level text refs (type == "ref" or type == "index"), deduplicated
    seen: set[str] = set()
    results: list[dict] = []
    for m in matches:
        ref = m.get("key") or m.get("ref") or m.get("title", "")
        if not ref or ref in seen:
            continue
        seen.add(ref)
        results.append({
            "ref": ref,
            "title": m.get("title", ref),
            "heTitle": m.get("heTitle", ""),
            "type": m.get("type", "ref"),
        })
    # If the name API returns nothing, fall back to the Elasticsearch search
    if not results:
        fallback_url = SEFARIA_SEARCH_API.format(query=encoded)
        async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
            resp = await client.get(fallback_url)
            if resp.status_code == 200:
                raw = resp.json().get("hits", {}).get("hits", [])
                for hit in raw[:10]:
                    src = hit.get("_source", {})
                    ref = src.get("ref", "")
                    if ref and ref not in seen:
                        seen.add(ref)
                        results.append({
                            "ref": ref,
                            "title": src.get("title", ref),
                            "heTitle": src.get("heTitle", ""),
                            "type": "ref",
                        })
    return results


# ── Text fetching ─────────────────────────────────────────────────────────────

def _looks_like_github_path(ref: str) -> bool:
    """
    Return True if *ref* looks like a Sefaria-Export GitHub path, e.g.:
        'Tanakh/Writings/Esther/Hebrew/Tanach with Ta'amei Hamikra'
    Simple refs like 'Esther' or 'Genesis 1' are not GitHub paths.
    """
    # A GitHub path always has at least three '/' separators
    return ref.count("/") >= 3


def _strip_html(value: Any) -> Any:
    """
    Recursively decode HTML entities and strip HTML tags from text values.
    Handles nested lists as returned by the Sefaria text API.

    For example: '&nbsp;&nbsp;וְאֵ֥ת&thinsp;' → '  וְאֵ֥ת '
    """
    if isinstance(value, str):
        value = html_lib.unescape(value)          # &nbsp; → \xa0, &thinsp; → \u2009, etc.
        value = re.sub(r"<[^>]+>", "", value)     # strip remaining <tags>
        value = value.replace("\xa0", " ")        # non-breaking space → space
        value = value.replace("\u2009", " ")      # thin space → space
        value = value.replace("\u200b", "")       # zero-width space → remove
        return value
    if isinstance(value, list):
        return [_strip_html(v) for v in value]
    return value


def _normalize_live_api_response(data: dict) -> dict:
    """
    The live Sefaria /api/texts/ response uses 'he' for Hebrew and 'text' for English.
    Sefaria-Export JSONs use 'text' for the primary (Hebrew) text.
    Rename 'he' → 'text' so the rest of the pipeline is consistent.
    Also strips HTML entities and tags which the live API injects into verse text.
    """
    if "he" in data:
        # Move live-API Hebrew content to 'text', keeping English under 'en'
        data["en"] = _strip_html(data.get("text", []))
        data["text"] = _strip_html(data.pop("he"))
    return data


async def pull_text(ref: str) -> dict[str, Any]:
    """
    Fetch a Sefaria text JSON by ref.
    - If *ref* is a full GitHub path (≥3 slashes), tries Sefaria-Export GitHub first.
    - Otherwise (or on 404), falls back to the live Sefaria /api/texts/ endpoint.
    """
    path = ref.replace(" ", "%20")
    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        if _looks_like_github_path(ref):
            url = GITHUB_TEXT_BASE.format(path=path)
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.json()
        # Fall back to live Sefaria API
        live_url = SEFARIA_TEXT_API.format(ref=path)
        resp = await client.get(live_url)
        resp.raise_for_status()
        return _normalize_live_api_response(resp.json())


def pull_text_sync(ref: str) -> dict[str, Any]:
    """
    Synchronous version of pull_text for use in Celery tasks.
    - If *ref* is a full GitHub path (≥3 slashes), tries Sefaria-Export GitHub first.
    - Otherwise (or on 404), falls back to the live Sefaria /api/texts/ endpoint.
    """
    path = ref.replace(" ", "%20")
    with httpx.Client(timeout=settings.http_timeout) as client:
        if _looks_like_github_path(ref):
            url = GITHUB_TEXT_BASE.format(path=path)
            resp = client.get(url)
            if resp.status_code == 200:
                return resp.json()
        # Fall back to live Sefaria API
        live_url = SEFARIA_TEXT_API.format(ref=path)
        resp = client.get(live_url)
        resp.raise_for_status()
        return _normalize_live_api_response(resp.json())


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
