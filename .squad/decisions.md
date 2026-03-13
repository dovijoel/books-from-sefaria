# Squad Decisions

## Active Decisions

### ADR-001: Tech Stack (2025-06-16)

- **Frontend:** Next.js 14 · App Router · TypeScript · Tailwind CSS · shadcn/ui
- **Backend:** FastAPI (Python 3.11) — matches existing Python notebook codebase
- **Async jobs:** Celery + Redis — PDF generation is 30s–3min; must be async
- **Database:** PostgreSQL — saved configurations and job history
- **PDF Engine:** LaTeX / texlive-full in Docker
- **Deployment:** Docker Compose — single `docker compose up` deploys everything

### ADR-002: Directory Layout (2025-06-16)

```
C:\repos\sefaria\
├── frontend/          # Next.js 14
├── backend/           # FastAPI + Celery workers
│   └── tests/         # pytest unit + integration
├── e2e/               # Playwright E2E tests
├── links/             # Commentary CSVs (from fork)
├── resources/         # LaTeX templates, fonts (from fork)
└── docker-compose.yml
```

### ADR-003: API Contract (2025-06-16)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/sefaria/search` | Search Sefaria text index |
| GET | `/api/v1/sefaria/text/{ref}` | Fetch text + chapter structure |
| POST | `/api/v1/jobs` | Submit PDF generation job |
| GET | `/api/v1/jobs/{job_id}` | Poll job status |
| GET | `/api/v1/jobs/{job_id}/download` | Download completed PDF |
| GET | `/api/v1/configs` | List saved configurations |
| POST | `/api/v1/configs` | Save a configuration |

## Governance

- All meaningful changes require team consensus
- Document architectural decisions here
- Inbox: `.squad/decisions/inbox/` (agents drop proposals; Scribe merges)
