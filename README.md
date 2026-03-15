# 📖 Sefaria Book Creator

> **Create beautifully typeset PDF books from Jewish texts on the [Sefaria](https://www.sefaria.org) platform.**

🌐 **Live site:** [sefariabookcreator.debuggingmadejoyful.tech](https://sefariabookcreator.debuggingmadejoyful.tech)

<!-- Screenshot placeholder -->
<!-- ![Sefaria Book Creator screenshot](docs/screenshot.png) -->

---

## ✨ Features

- 🔍 **Browse & select** any text from the Sefaria library
- ⚙️ **Flexible configuration** — choose commentaries, fonts, layout, and page size
- 📄 **Professional PDF output** — powered by XeLaTeX/texlive for publication-quality typesetting
- 🔤 **Hebrew/English bilingual** support with proper RTL rendering
- 💾 **Save configurations** so you can regenerate a book at any time
- 📊 **Job history** — track previous builds and download past PDFs
- ⚡ **Async generation** — long jobs run in the background via Celery; the UI updates live

---

## 🚀 Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (v24+)
- [Git](https://git-scm.com/)

### 1 — Clone the repository

```bash
git clone https://github.com/dovijoel/books-from-sefaria.git
cd books-from-sefaria
```

### 2 — Configure environment variables

```bash
cp .env.example .env
# Edit .env and set a strong SECRET_KEY
```

Generate a secure key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3 — Start the stack

```bash
docker compose up --build
```

| Service  | URL                    |
|----------|------------------------|
| Frontend | http://localhost:3000  |
| Backend  | http://localhost:8000  |
| API docs | http://localhost:8000/docs |

### 4 — Run database migrations

```bash
docker compose exec backend alembic upgrade head
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                               │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP / WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│               Next.js 14 (App Router)                        │
│           TypeScript · Tailwind CSS · shadcn/ui              │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API calls
┌──────────────────────▼──────────────────────────────────────┐
│                  FastAPI (Python 3.11)                        │
│           Pydantic · SQLAlchemy · Alembic                     │
└────┬───────────────────────────────────────┬────────────────┘
     │ enqueue job                           │ read/write
┌────▼────────┐                    ┌─────────▼──────────┐
│    Redis    │                    │     PostgreSQL      │
│  (broker)   │                    │  (configs, jobs)    │
└────┬────────┘                    └────────────────────┘
     │ dequeue
┌────▼─────────────────────────────────────────────────┐
│              Celery Worker                            │
│   Python pipeline → XeLaTeX → PDF                    │
│   Reads: /app/links, /app/resources                  │
└──────────────────────────────────────────────────────┘
```

**Key design decisions:**

| Concern | Choice | Reason |
|---------|--------|--------|
| Async jobs | Celery + Redis | PDF generation can take 30 s – 3 min |
| PDF engine | XeLaTeX (texlive-full) | Superior Hebrew/RTL support |
| Database | PostgreSQL | JSONB for flexible book configs |
| Frontend | Next.js App Router | RSC + streaming for live job status |

---

## 🛠️ Development Workflow

### Using Make

```bash
make dev          # start full stack with hot reload
make build        # rebuild Docker images
make down         # stop all containers
make logs         # tail all service logs
make migrate      # run Alembic migrations
make shell-backend # bash shell inside the backend container
```

### Working on the frontend only

```bash
cd frontend
npm install
npm run dev       # http://localhost:3000 (proxies API to localhost:8000)
```

### Working on the backend only

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Adding a database migration

```bash
# 1. Edit your SQLAlchemy models in backend/app/models/
# 2. Generate the migration
docker compose exec backend alembic revision --autogenerate -m "describe your change"
# 3. Apply it
docker compose exec backend alembic upgrade head
```

---

## 🧪 Testing

```bash
make test-backend    # pytest (unit + integration)
make test-frontend   # Jest / React Testing Library
make test-e2e        # Playwright end-to-end tests
```

Run backend tests locally (no Docker):

```bash
cd backend
pytest tests/ -v
```

---

## 📁 Project Structure

```
sefaria-book-creator/
├── backend/               # FastAPI application
│   ├── app/
│   │   ├── api/v1/        # Route handlers
│   │   ├── models/        # SQLAlchemy ORM models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── workers/       # Celery tasks
│   ├── alembic/           # Database migrations
│   ├── tests/
│   └── requirements.txt
├── frontend/              # Next.js 14 application
├── e2e/                   # Playwright tests
├── links/                 # Commentary linkage CSVs (read-only)
├── resources/             # LaTeX templates & assets (read-only)
├── docker-compose.yml
├── Makefile
└── .env.example
```

---

## 🤝 Contributing & Issues

**GitHub:** [github.com/dovijoel/books-from-sefaria](https://github.com/dovijoel/books-from-sefaria)

Found a bug? Have a feature request? [Open an issue](https://github.com/dovijoel/books-from-sefaria/issues) — contributions and feedback are welcome!

### How to contribute

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Commit your changes: `git commit -m "feat: add my feature"`
4. Push to your branch: `git push origin feat/my-feature`
5. Open a Pull Request

Please follow [Conventional Commits](https://www.conventionalcommits.org/) and ensure all tests pass before submitting a PR.

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

### Text Content Attribution

The Jewish texts accessed through this application are provided by the [Sefaria](https://www.sefaria.org) platform. Sefaria's own translations and original content are released under a [CC-BY-NC](https://creativecommons.org/licenses/by-nc/4.0/) (Creative Commons Attribution-NonCommercial) license. Public domain source texts (e.g., Torah, Talmud, classical commentaries) remain in the public domain. Please review [Sefaria's terms of use](https://www.sefaria.org/terms) for full details on content licensing.

This tool generates PDFs from Sefaria's API for personal and educational use. If you plan to distribute generated content commercially, verify compliance with Sefaria's licensing terms.

---

*Built with ❤️ on top of [nkasimer/books-from-sefaria](https://github.com/nkasimer/books-from-sefaria) and the [Sefaria Open Book Project](https://www.sefaria.org/texts).*
 
