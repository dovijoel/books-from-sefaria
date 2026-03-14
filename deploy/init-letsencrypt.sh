#!/usr/bin/env bash
# =============================================================================
# SSL Certificate Setup with Let's Encrypt (Certbot)
# =============================================================================
# Run this AFTER deploy.sh, once you have a domain pointing to your server.
#
# Usage:
#   sudo ./deploy/init-letsencrypt.sh your-domain.com your-email@example.com
# =============================================================================

set -euo pipefail

DOMAIN="${1:?Usage: $0 <domain> <email>}"
EMAIL="${2:?Usage: $0 <domain> <email>}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COMPOSE_FILE="$PROJECT_DIR/docker-compose.prod.yml"
ENV_FILE="$PROJECT_DIR/.env.production"

echo "Setting up SSL for: $DOMAIN"

# Stop nginx temporarily
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" stop nginx

# Get certificate using standalone mode
docker run --rm -p 80:80 \
    -v sefaria_certbot-conf:/etc/letsencrypt \
    -v sefaria_certbot-www:/var/www/certbot \
    certbot/certbot certonly \
    --standalone \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    -d "$DOMAIN"

echo ""
echo "Certificate obtained! Now update nginx config:"
echo ""
echo "1. Edit nginx/nginx.conf:"
echo "   - Uncomment the HTTPS server block at the bottom"
echo "   - Replace YOUR_DOMAIN with: $DOMAIN"
echo "   - Uncomment the HTTP→HTTPS redirect in the port 80 block"
echo ""
echo "2. Update .env.production:"
echo "   - Set NEXT_PUBLIC_API_URL=https://$DOMAIN"
echo ""
echo "3. Rebuild and restart:"
echo "   docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build nginx frontend"
echo ""
echo "4. Set up auto-renewal (add to crontab):"
echo '   0 3 * * * docker run --rm -v sefaria_certbot-conf:/etc/letsencrypt certbot/certbot renew --quiet && docker compose -f /path/to/docker-compose.prod.yml restart nginx'
echo ""

# Restart nginx
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" start nginx
