# ──────────────────────────────────────────────
# Sefaria Book Creator — Backend Dockerfile
# Base: python:3.11-slim
# Includes: texlive-full for LaTeX PDF generation
# ──────────────────────────────────────────────
FROM python:3.11-slim AS base

# Prevent interactive prompts during package installs
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# ── System dependencies + LaTeX toolchain ────
# texlive-full is large (~4 GB); install with no-recommends and clean cache
# immediately to keep layers as small as possible.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        latexmk \
        texlive-full \
        texlive-xetex \
        texlive-fonts-extra \
        texlive-latex-extra \
        culmus \
        fonts-sil-ezra \
        fonts-noto-core \
    && \
    # Make TeX-distributed fonts visible to fontconfig / XeLaTeX
    mkdir -p /etc/fonts/conf.d && \
    echo '<?xml version="1.0"?>' > /etc/fonts/conf.d/09-texlive-fonts.conf && \
    echo '<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">' >> /etc/fonts/conf.d/09-texlive-fonts.conf && \
    echo '<fontconfig>' >> /etc/fonts/conf.d/09-texlive-fonts.conf && \
    echo '  <dir>/usr/share/texlive/texmf-dist/fonts/opentype</dir>' >> /etc/fonts/conf.d/09-texlive-fonts.conf && \
    echo '  <dir>/usr/share/texlive/texmf-dist/fonts/truetype</dir>' >> /etc/fonts/conf.d/09-texlive-fonts.conf && \
    echo '</fontconfig>' >> /etc/fonts/conf.d/09-texlive-fonts.conf && \
    fc-cache -fv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

# ── Python dependencies ───────────────────────
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ── Application code ──────────────────────────
COPY backend/ .

# links/ and resources/ are bind-mounted at runtime:
#   /app/links      ← ./links
#   /app/resources  ← ./resources

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
