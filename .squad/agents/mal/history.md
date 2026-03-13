# Project Context

- **Owner:** Dovi Joel
- **Project:** Sefaria Book Creator Web App — a full-stack web application that lets users create beautifully typeset PDF books from Jewish texts on the Sefaria platform. Based on the Python/LaTeX pipeline in `nkasimer/books-from-sefaria` (forked to `dovijoel/books-from-sefaria`).
- **Stack:** Next.js 14 (App Router, TypeScript, Tailwind CSS, shadcn/ui) · FastAPI (Python 3.11) · Celery + Redis (async jobs) · PostgreSQL · LaTeX/texlive (PDF generation) · Docker Compose
- **Created:** 2025-06-16

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->

- The core PDF generation is LaTeX-based — must run `pdflatex` in a container with texlive-full installed. This is slow (30s–3min) so all generation jobs MUST be async via Celery.
- Text data is pulled from `https://raw.githubusercontent.com/Sefaria/Sefaria-Export/refs/heads/master/json/{text_path}.json` — no API key needed.
- Commentary linkage data is in local CSVs (`links/links0.csv` through `links/links8.csv`) — these must be bundled with the backend container.
- The `book_settings.json` schema is the complete configuration spec — the UI must expose all configurable fields.
- The repo is at: `C:\repos\sefaria` (also `https://github.com/dovijoel/books-from-sefaria`)
