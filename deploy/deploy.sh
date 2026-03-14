#!/usr/bin/env bash
# =============================================================================
# Deploy / Update Script for Sefaria Book Creator
# =============================================================================
# Builds and deploys (or updates) the production stack.
#
# Usage:
#   ./deploy/deploy.sh              # Full deploy (build + start)
#   ./deploy/deploy.sh --no-build   # Restart without rebuilding
#   ./deploy/deploy.sh --pull       # Pull latest code first
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.prod.yml"
ENV_FILE="$PROJECT_DIR/.env.production"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()   { echo -e "${GREEN}[DEPLOY]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# Parse args
DO_BUILD=true
DO_PULL=false
for arg in "$@"; do
    case $arg in
        --no-build) DO_BUILD=false ;;
        --pull)     DO_PULL=true ;;
        *)          warn "Unknown argument: $arg" ;;
    esac
done

cd "$PROJECT_DIR"

# --- Pre-flight checks ---
log "Running pre-flight checks..."

if [ ! -f "$ENV_FILE" ]; then
    error ".env.production not found!"
    error "Copy .env.production.example to .env.production and fill in values."
    exit 1
fi

if ! command -v docker &> /dev/null; then
    error "Docker not installed. Run: sudo ./deploy/setup-server.sh"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    error "Docker Compose V2 not found."
    exit 1
fi

# Check required env vars
source "$ENV_FILE"
if [ "${SECRET_KEY:-}" = "CHANGE_ME_TO_A_LONG_RANDOM_STRING_64_CHARS" ] || [ -z "${SECRET_KEY:-}" ]; then
    error "SECRET_KEY not set in .env.production!"
    exit 1
fi
if [ "${POSTGRES_PASSWORD:-}" = "CHANGE_ME_STRONG_PASSWORD" ] || [ -z "${POSTGRES_PASSWORD:-}" ]; then
    error "POSTGRES_PASSWORD not set in .env.production!"
    exit 1
fi

log "Pre-flight checks passed ✓"

# --- Pull latest code ---
if [ "$DO_PULL" = true ]; then
    log "Pulling latest code..."
    git pull --ff-only
fi

# --- Build ---
if [ "$DO_BUILD" = true ]; then
    log "Building Docker images (this may take 15-30 minutes on first run)..."
    docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build
fi

# --- Deploy ---
log "Starting services..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d

# --- Wait for health ---
log "Waiting for services to be healthy..."
sleep 10

RETRIES=30
for i in $(seq 1 $RETRIES); do
    if curl -sf http://localhost/health > /dev/null 2>&1; then
        log "Backend healthy ✓"
        break
    fi
    if [ "$i" -eq "$RETRIES" ]; then
        warn "Backend health check timed out after ${RETRIES}0 seconds"
        warn "Check logs with: docker compose -f docker-compose.prod.yml logs backend"
    fi
    sleep 10
done

# --- Status ---
echo ""
log "========================================="
log " Deployment Complete!"
log "========================================="
echo ""
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
echo ""
PUBLIC_IP=$(curl -sf http://ifconfig.me 2>/dev/null || echo "YOUR_IP")
log "Application should be available at: http://${PUBLIC_IP}"
log ""
log "Useful commands:"
log "  Logs:    docker compose -f docker-compose.prod.yml --env-file .env.production logs -f"
log "  Stop:    docker compose -f docker-compose.prod.yml --env-file .env.production down"
log "  Update:  ./deploy/deploy.sh --pull"
echo ""
