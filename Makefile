# =============================================================
# Sefaria Book Creator — Developer Makefile
# =============================================================
.DEFAULT_GOAL := help
COMPOSE = docker compose

.PHONY: help up dev build down logs \
        test-backend test-frontend test-e2e \
        migrate shell-backend \
        prod-up prod-down prod-logs prod-status prod-restart

help:          ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Stack lifecycle ──────────────────────────────────────────
up:            ## Build images and start all services in detached mode
	$(COMPOSE) up --build -d

dev:           ## Start full stack in development mode (hot reload)
	@cp -n .env.example .env 2>/dev/null || true
	$(COMPOSE) up --build

build:         ## Build (or rebuild) all Docker images
	$(COMPOSE) build

down:          ## Stop and remove all containers
	$(COMPOSE) down

logs:          ## Tail logs from all services
	$(COMPOSE) logs -f

# ── Testing ───────────────────────────────────────────────────
test-backend:  ## Run backend unit + integration tests inside the container
	$(COMPOSE) run --rm backend pytest backend/tests -v

test-frontend: ## Run Next.js tests
	$(COMPOSE) run --rm frontend npm test -- --watchAll=false

test-e2e:      ## Run Playwright end-to-end tests
	$(COMPOSE) run --rm frontend npx playwright test

# ── Database ──────────────────────────────────────────────────
migrate:       ## Apply Alembic database migrations
	$(COMPOSE) run --rm backend alembic upgrade head

# ── Shells ────────────────────────────────────────────────────
shell-backend: ## Open an interactive shell in the backend container
	$(COMPOSE) exec backend /bin/bash

# ── Production ────────────────────────────────────────────────
PROD_COMPOSE = docker compose -f docker-compose.prod.yml --env-file .env.production

prod-up:       ## Build and start production stack
	$(PROD_COMPOSE) up --build -d

prod-down:     ## Stop and remove production containers
	$(PROD_COMPOSE) down

prod-logs:     ## Tail production logs
	$(PROD_COMPOSE) logs -f

prod-status:   ## Show running production containers
	$(PROD_COMPOSE) ps

prod-restart:  ## Restart production without rebuilding
	$(PROD_COMPOSE) restart
