# Project Context

- **Owner:** Dovi Joel
- **Project:** Sefaria Book Creator Web App — a full-stack web application that lets users create beautifully typeset PDF books from Jewish texts on the Sefaria platform. Based on the Python/LaTeX pipeline in `nkasimer/books-from-sefaria` (forked to `dovijoel/books-from-sefaria`).
- **Stack:** Next.js 14 (App Router, TypeScript, Tailwind CSS, shadcn/ui) · FastAPI (Python 3.11) · Celery + Redis (async jobs) · PostgreSQL · LaTeX/texlive (PDF generation) · Docker Compose
- **Created:** 2025-06-16

## Learnings

<!-- Append new learnings below. Each entry is something lasting about the project. -->

- PDF generation is async via Celery — E2E tests must use polling/waiting for job completion, not just fire-and-forget.
- The Sefaria API is external and rate-limited — backend tests must mock HTTP calls to Sefaria to avoid flakiness.
- LaTeX compilation can be slow in CI — consider separate test environments: fast (no PDF) and slow (full PDF generation).
- Hebrew RTL rendering needs Playwright screenshot tests to catch visual regressions.
- The repo is at: `C:\repos\sefaria` (also `https://github.com/dovijoel/books-from-sefaria`)
