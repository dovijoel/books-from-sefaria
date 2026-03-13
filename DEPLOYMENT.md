# Deployment Guide

## Prerequisites
- Docker Desktop 24+ (or Docker Engine + Docker Compose V2)
- Git
- 8 GB RAM minimum (texlive-full image is ~4 GB)
- 20 GB disk space

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/dovijoel/books-from-sefaria.git
cd books-from-sefaria
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env if needed (defaults work for local dev)
```

### 3. Build and start all services
```bash
make up
# Or: docker compose up --build -d
```

> **Note:** The first build is slow (~10–15 minutes) because the backend image
> installs `texlive-full` (~4 GB) for LaTeX PDF generation.

### 4. Run database migrations
```bash
make migrate
# Or: docker compose exec backend alembic upgrade head
```

### 5. Access the app
| Endpoint | URL |
|----------|-----|
| Frontend UI | http://localhost:3000 |
| Backend API docs | http://localhost:8000/docs |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://sefaria:sefaria@postgres:5432/sefaria` | PostgreSQL connection string |
| `REDIS_URL` | `redis://redis:6379/0` | Redis connection for Celery |
| `CELERY_BROKER_URL` | `redis://redis:6379/0` | Celery task broker |
| `CELERY_RESULT_BACKEND` | `redis://redis:6379/1` | Celery result store |
| `SECRET_KEY` | *(must be set)* | App secret — generate with `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ENVIRONMENT` | `development` | `development` or `production` |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `PDF_OUTPUT_DIR` | `/tmp/pdf_output` | Container path for generated PDFs |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend URL used by the browser |

Copy `.env.example` to `.env` and edit before first run. The `.env` file is
git-ignored — never commit it.

---

## Services

| Service | Port | Description |
|---------|------|-------------|
| `frontend` | 3000 | Next.js web UI (hot-reload in dev, standalone in prod) |
| `backend` | 8000 | FastAPI REST API + Alembic migrations |
| `worker` | — | Celery PDF-generation worker (shares backend image) |
| `postgres` | 5432 | PostgreSQL 15 database |
| `redis` | 6379 | Redis 7 message broker and result backend |

---

## Volume Mounts

| Host path | Container path | Purpose |
|-----------|----------------|---------|
| `./links` | `/app/links` | CSV link files for Sefaria commentary (read-only) |
| `./resources` | `/app/resources` | Static assets used by LaTeX (read-only) |
| `/tmp/pdf_output` | `/tmp/pdf_output` | Generated PDF output (shared between backend & worker) |
| `postgres_data` | `/var/lib/postgresql/data` | Persistent database storage |
| `redis_data` | `/data` | Persistent Redis storage |

---

## Production Deployment

Update `.env` with production values:

```bash
DATABASE_URL=postgresql://user:password@your-db-host:5432/sefaria
REDIS_URL=redis://your-redis-host:6379/0
CELERY_BROKER_URL=redis://your-redis-host:6379/0
CELERY_RESULT_BACKEND=redis://your-redis-host:6379/1
SECRET_KEY=<long-random-hex>
ENVIRONMENT=production
NEXT_PUBLIC_API_URL=https://your-domain.com
```

Additional production considerations:

- Run behind an **Nginx reverse proxy** for TLS termination.
- Use **Let's Encrypt / Certbot** for SSL certificates.
- Use a managed **PostgreSQL** service (e.g., RDS, Cloud SQL) for durability.
- Use a managed **Redis** service (e.g., ElastiCache, Upstash) for HA.
- Push built images to a **container registry** (Docker Hub, GHCR, ECR) so
  workers can pull without rebuilding.
- Set `output: "standalone"` in `next.config.js` and use the `runner` stage of
  the frontend Dockerfile for the production image.

---

## Useful Commands

```bash
make up              # Build images and start all services (detached)
make down            # Stop and remove all containers
make logs            # Follow logs from all services
make migrate         # Run Alembic database migrations
make test-backend    # Run backend pytest suite inside the container
make test-frontend   # Run Next.js / Jest tests inside the container
make shell-backend   # Open an interactive shell in the backend container
make build           # Rebuild all Docker images without starting
```
