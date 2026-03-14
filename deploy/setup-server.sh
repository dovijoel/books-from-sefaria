#!/usr/bin/env bash
# =============================================================================
# Server Setup Script for Oracle Cloud Free Tier (Ubuntu 22.04 / Oracle Linux 8)
# =============================================================================
# Run this ONCE on a fresh VM to install Docker and prepare for deployment.
#
# Usage:
#   chmod +x deploy/setup-server.sh
#   sudo ./deploy/setup-server.sh
# =============================================================================

set -euo pipefail

echo "========================================="
echo " Sefaria Book Creator — Server Setup"
echo "========================================="

# Detect OS
if [ -f /etc/oracle-release ] || [ -f /etc/redhat-release ]; then
    OS_FAMILY="rhel"
    echo "Detected: Oracle Linux / RHEL"
elif [ -f /etc/lsb-release ] || [ -f /etc/debian_version ]; then
    OS_FAMILY="debian"
    echo "Detected: Ubuntu / Debian"
else
    echo "Unsupported OS. Please use Ubuntu 22.04 or Oracle Linux 8."
    exit 1
fi

# --- 1. System updates ---
echo ""
echo "[1/6] Updating system packages..."
if [ "$OS_FAMILY" = "debian" ]; then
    apt-get update -qq && apt-get upgrade -y -qq
elif [ "$OS_FAMILY" = "rhel" ]; then
    dnf update -y -q
fi

# --- 2. Install Docker ---
echo ""
echo "[2/6] Installing Docker..."
if command -v docker &> /dev/null; then
    echo "Docker already installed: $(docker --version)"
else
    if [ "$OS_FAMILY" = "debian" ]; then
        apt-get install -y -qq ca-certificates curl gnupg lsb-release
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
            gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        chmod a+r /etc/apt/keyrings/docker.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
            https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" > \
            /etc/apt/sources.list.d/docker.list
        apt-get update -qq
        apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    elif [ "$OS_FAMILY" = "rhel" ]; then
        dnf install -y -q dnf-utils
        dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        dnf install -y -q docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        systemctl start docker
    fi
    systemctl enable docker
    echo "Docker installed: $(docker --version)"
fi

# --- 3. Add current user to docker group ---
echo ""
echo "[3/6] Configuring Docker permissions..."
DEPLOY_USER="${SUDO_USER:-$(whoami)}"
if [ "$DEPLOY_USER" != "root" ]; then
    usermod -aG docker "$DEPLOY_USER"
    echo "Added $DEPLOY_USER to docker group (re-login required)"
fi

# --- 4. Create swap file (important for Free Tier builds) ---
echo ""
echo "[4/6] Setting up swap space..."
if [ -f /swapfile ]; then
    echo "Swap already exists: $(swapon --show)"
else
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "4GB swap file created"
fi

# --- 5. Configure firewall ---
echo ""
echo "[5/6] Configuring firewall..."
if [ "$OS_FAMILY" = "debian" ]; then
    if command -v ufw &> /dev/null; then
        ufw allow 22/tcp
        ufw allow 80/tcp
        ufw allow 443/tcp
        ufw --force enable
        echo "UFW configured (SSH, HTTP, HTTPS)"
    fi
elif [ "$OS_FAMILY" = "rhel" ]; then
    if command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-service=http
        firewall-cmd --permanent --add-service=https
        firewall-cmd --permanent --add-service=ssh
        firewall-cmd --reload
        echo "firewalld configured (SSH, HTTP, HTTPS)"
    fi
fi

# --- 6. Install useful tools ---
echo ""
echo "[6/6] Installing utilities..."
if [ "$OS_FAMILY" = "debian" ]; then
    apt-get install -y -qq git htop curl jq
elif [ "$OS_FAMILY" = "rhel" ]; then
    dnf install -y -q git htop curl jq
fi

echo ""
echo "========================================="
echo " Setup Complete!"
echo "========================================="
echo ""
echo "IMPORTANT: Oracle Cloud also requires opening ports in the"
echo "VCN Security List. Go to:"
echo "  Networking > Virtual Cloud Networks > your-vcn > Security Lists"
echo "  Add Ingress Rules for ports 80 and 443 (0.0.0.0/0, TCP)"
echo ""
echo "Next steps:"
echo "  1. Log out and back in (for docker group)"
echo "  2. Clone the repo:  git clone https://github.com/YOUR_USER/books-from-sefaria.git"
echo "  3. cd books-from-sefaria"
echo "  4. cp .env.production.example .env.production"
echo "  5. Edit .env.production with your settings"
echo "  6. Run: ./deploy/deploy.sh"
echo ""
