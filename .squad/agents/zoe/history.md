# Project Context

- **Owner:** Dovi Joel
- **Project:** Sefaria Book Creator Web App — a full-stack web application that lets users create beautifully typeset PDF books from Jewish texts on the Sefaria platform. Based on the Python/LaTeX pipeline in `nkasimer/books-from-sefaria` (forked to `dovijoel/books-from-sefaria`).
- **Stack:** Next.js 14 (App Router, TypeScript, Tailwind CSS, shadcn/ui) · FastAPI (Python 3.11) · Celery + Redis (async jobs) · PostgreSQL · LaTeX/texlive (PDF generation) · Docker Compose
- **Created:** 2025-06-16

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->

- The core notebook logic is in `script_to_make_latex.ipynb` — must be ported to clean Python modules in `backend/app/services/`.
- Key functions to port: `pull_text()`, `pull_links()`, `match_comment()`, `get_index_json()`, `find_perek()`, `match_chapters()`
- Text fetched from: `https://raw.githubusercontent.com/Sefaria/Sefaria-Export/refs/heads/master/json/{text_path}.json`
- Commentary linkage CSVs are in `links/` directory — must be bundled into the backend container
- LaTeX compilation requires `pdflatex` with `polyglossia` and Hebrew font packages — use `texlive-full` in Docker
- Python deps from original: `python-hebrew-numbers`, `pdfrw`, `json`, `urllib`, `math`, `csv`, `subprocess`
- The repo is at: `C:\repos\sefaria` (also `https://github.com/dovijoel/books-from-sefaria`)
