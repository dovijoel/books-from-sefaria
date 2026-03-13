"""
Sefaria data-fetching service – ported from notebook cells 2–8, 19.

All HTTP calls use httpx.  pull_links() reads local CSV files.
"""
from __future__ import annotations

import csv
import os
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
SEFARIA_NAME_API = "https://www.sefaria.org/api/name/{query}"


# ── HTTP helpers ──────────────────────────────────────────────────────────────

def pull_text(string_for_link: str) -> dict[str, Any]:
    """Fetch a Sefaria text JSON by path (spaces → %20)."""
    path = string_for_link.replace(" ", "%20")
    url = GITHUB_TEXT_BASE.format(path=path)
    with httpx.Client(timeout=settings.http_timeout) as client:
        resp = client.get(url)
        resp.raise_for_status()
        return resp.json()


def get_index_json(masekhet: str) -> list[dict]:
    """Return the Chapters nodes for a masekhet (spaces → underscores)."""
    name = masekhet.replace(" ", "_")
    url = GITHUB_SCHEMA_BASE.format(masekhet=name)
    with httpx.Client(timeout=settings.http_timeout) as client:
        resp = client.get(url)
        resp.raise_for_status()
        data = resp.json()
    return data["alts"]["Chapters"]["nodes"]


async def search_names(query: str) -> dict[str, Any]:
    """Call Sefaria name API and return raw JSON."""
    url = SEFARIA_NAME_API.format(query=query.replace(" ", "%20"))
    async with httpx.AsyncClient(timeout=settings.http_timeout) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


# ── Links ─────────────────────────────────────────────────────────────────────

def pull_links(links_dir: str | None = None) -> list[list[str]]:
    """
    Load commentary links from links0.csv … links8.csv.
    Returns list of [citation1, citation2] pairs.
    """
    base = links_dir or settings.links_dir
    result: list[list[str]] = []
    for i in range(9):
        path = os.path.join(base, f"links{i}.csv")
        if not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if len(row) >= 3 and row[2] == "commentary":
                    result.append([row[0], row[1]])
    return result


# ── Commentary matching ───────────────────────────────────────────────────────

def match_comment(comment_str: str, links: list[list[str]]) -> str | None:
    """Return the ref that *comment_str* is linked to, or None."""
    for link in links:
        if comment_str in link[0]:
            return link[1]
        if comment_str in link[1]:
            return link[0]
    return None


# ── Perek / chapter lookup ────────────────────────────────────────────────────

def find_perek(name: str) -> tuple[str, str]:
    """
    Given a ref string, return (en_chapter_title, he_chapter_title).
    Falls back to the ref string if nothing is found.
    """
    if " on " in name:
        name = name.split(" on ")[1]
    parts = name.split()
    if len(parts) < 2:
        return name, name
    masekhet = parts[0]
    daf_part = parts[1]
    try:
        chapters = get_index_json(masekhet)
    except Exception:
        return name, name
    for chapter in chapters:
        refs = chapter.get("refs", [])
        for ref in refs:
            if daf_part in ref:
                return chapter.get("title", name), chapter.get("heTitle", name)
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
        # Construct the ref for this daf position
        daf_num = int((current_daf + 1) / 2)
        amud = "a" if current_daf % 2 == 1 else "b"
        ref = f"{ref_base} {daf_num}{amud}"
        # Determine the chapter for this daf
        commentary_ref = match_comment(ref, links)
        if commentary_ref:
            title_en, title_he = find_perek(commentary_ref)
        else:
            title_en, title_he = find_perek(ref)

        # Inject chapter marker if this looks like a new chapter
        if not new_text or (
            isinstance(new_text[-1], dict)
            and new_text[-1].get("name_en") != title_en
        ):
            if title_en != ref:  # only inject if we found a real chapter name
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
