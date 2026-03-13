# Squad Team

> Sefaria Book Creator Web App

## Coordinator

| Name | Role | Notes |
|------|------|-------|
| Squad | Coordinator | Routes work, enforces handoffs and reviewer gates. |

## Members

| Name | Role | Charter | Status |
|------|------|---------|--------|
| Mal | Tech Lead / Architect | [charter](.squad/agents/mal/charter.md) | Active |
| Kaylee | Frontend Developer | [charter](.squad/agents/kaylee/charter.md) | Active |
| Zoe | Backend Developer | [charter](.squad/agents/zoe/charter.md) | Active |
| Wash | QA / Test Engineer | [charter](.squad/agents/wash/charter.md) | Active |
| Scribe | Session Logger | — (built-in) | Active |
| Ralph | Performance Monitor | — (built-in) | Active |

## @copilot Capability Profile

🟢 **Good fit for @copilot:**
- Adding a new API endpoint that follows existing patterns
- Writing or updating unit/integration tests
- Fixing a bug with a clear reproduction case and bounded scope
- Adding UI components that match the established design system
- Updating configuration files, env vars, Docker Compose tweaks
- Documentation and README updates

🟡 **Needs review:**
- New feature with clear requirements but non-trivial UI changes
- Refactoring existing modules with full test coverage

🔴 **Not suitable for @copilot:**
- Architecture or system design decisions
- Anything touching auth, access control, or secrets
- Decisions about which texts/commentary to support (requires product judgment)
- Changes to the LaTeX compilation pipeline without explicit test coverage

## Project Context

- **Project:** Sefaria Book Creator Web App
- **Description:** Full-stack web application for creating beautifully typeset PDF books from Jewish texts on the Sefaria platform. Built on the Python/LaTeX pipeline from `nkasimer/books-from-sefaria` (forked to `dovijoel/books-from-sefaria`).
- **Owner:** Dovi Joel (dovijoel)
- **Stack:** Next.js 14 (App Router, TypeScript, Tailwind CSS, shadcn/ui) · FastAPI · Celery + Redis · PostgreSQL · LaTeX/texlive · Docker Compose
- **Repo:** https://github.com/dovijoel/books-from-sefaria
- **Local path:** C:\repos\sefaria
- **Created:** 2025-06-16
