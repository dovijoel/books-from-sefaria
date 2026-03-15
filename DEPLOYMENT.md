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

## Production Deployment (Oracle Cloud Free Tier)

The production stack uses a separate `docker-compose.prod.yml` with:
- **Nginx** reverse proxy (TLS termination, rate limiting)
- **Production-optimized** frontend (standalone Next.js build)
- **No hot-reload** on backend
- **Resource limits** tuned for Oracle Free Tier (ARM Ampere A1)

### Step 1: Provision the Server

1. Create an Oracle Cloud Always Free ARM instance:
   - Shape: `VM.Standard.A1.Flex` (up to 4 OCPUs, 24 GB RAM)
   - OS: Ubuntu 22.04 (recommended) or Oracle Linux 8
   - Boot volume: 47 GB (default)
2. Open **ports 80 and 443** in your VCN Security List:
   - Networking → Virtual Cloud Networks → your-vcn → Security Lists
   - Add Ingress Rules: `0.0.0.0/0`, TCP, ports 80 and 443

### Step 2: Set Up the Server

```bash
# SSH into your instance
ssh ubuntu@YOUR_PUBLIC_IP

# Clone the repo
git clone https://github.com/dovijoel/books-from-sefaria.git
cd books-from-sefaria

# Run server setup (installs Docker, swap, firewall)
chmod +x deploy/setup-server.sh
sudo ./deploy/setup-server.sh

# Log out and back in (for docker group)
exit
ssh ubuntu@YOUR_PUBLIC_IP
cd books-from-sefaria
```

### Step 3: Configure Environment

```bash
cp .env.production.example .env.production
```

Edit `.env.production` with real values:

```bash
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
POSTGRES_PASSWORD=$(python3 -c "import secrets; print(secrets.token_hex(16))")

# Set these in .env.production:
# SECRET_KEY=<generated above>
# POSTGRES_PASSWORD=<generated above>
# DATABASE_URL=postgresql://sefaria:<password>@db:5432/sefaria_books
# NEXT_PUBLIC_API_URL=http://YOUR_PUBLIC_IP  (or https://your-domain.com)
```

### Step 4: Deploy

```bash
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

> **First build takes 20–40 minutes** (texlive-full is ~4 GB).
> Subsequent builds use cached layers and are much faster.

### Step 5: SSL (Optional — requires a domain)

```bash
chmod +x deploy/init-letsencrypt.sh
sudo ./deploy/init-letsencrypt.sh your-domain.com your@email.com
# Then follow the instructions to enable HTTPS in nginx.conf
```

### Updating

```bash
cd books-from-sefaria
./deploy/deploy.sh --pull    # Pulls latest code, rebuilds, restarts
```

---

## Architecture (Production)

```
                    ┌──────────┐
    Internet ──────▶│  Nginx   │:80/:443
                    └────┬─────┘
                    ┌────┴─────┐
              ┌─────┤ frontend │:3000  (Next.js standalone)
              │     └──────────┘
              │     ┌──────────┐
              └─────┤ backend  │:8000  (FastAPI, 2 workers)
                    └────┬─────┘
                    ┌────┴─────┐
              ┌─────┤  worker  │       (Celery, texlive)
              │     └──────────┘
         ┌────┴────┐  ┌───────┐
         │ postgres │  │ redis │
         └─────────┘  └───────┘
```

---

## Useful Commands

### Development
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

### Production
```bash
make prod-up         # Build and start production stack
make prod-down       # Stop production stack
make prod-logs       # Tail production logs
make prod-status     # Show running production containers
make prod-restart    # Restart without rebuilding
```
