FROM python:3.12-slim AS base

LABEL maintainer="Carlos Delfino <consultoria@carlosdelfino.eti.br"
LABEL description="AgenticSpace Sandbox - Web Scraping, Data Extraction, Feed Search & RSS Syndication CLI toolkit"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PLAYWRIGHT_BROWSERS_PATH=/opt/playwright-browsers \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# ─── System packages ───────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    jq \
    ca-certificates \
    gnupg \
    unzip \
    xz-utils \
    build-essential \
    libxml2 \
    libxslt1.1 \
    libxml2-utils \
    libssl-dev \
    libffi-dev \
    libcurl4-openssl-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# ─── htmlq (Rust HTML CSS-selector CLI) ────────────────────────────
RUN curl -sSL https://github.com/mgdm/htmlq/releases/latest/download/htmlq-x86_64-unknown-linux-musl.tar.gz \
    | tar xz -C /usr/local/bin htmlq 2>/dev/null \
    || echo "htmlq binary fetch skipped (will retry)" \
    && chmod +x /usr/local/bin/htmlq 2>/dev/null || true

# ─── Xidel (HTML/XML XPath & CSS selector CLI) ─────────────────────
RUN cd /tmp \
    && curl -sSL -o xidel.tar.gz "https://sourceforge.net/projects/videlibri/files/Xidel/Xidel%200.9.8/xidel-0.9.8-linux64.tar.gz/download" \
    && tar xzf xidel.tar.gz -C /tmp/xidel-extract 2>/dev/null || (mkdir -p /tmp/xidel-extract && tar xzf xidel.tar.gz -C /tmp/xidel-extract) \
    && find /tmp/xidel-extract -name 'xidel' -type f -executable -exec cp {} /usr/local/bin/xidel \; \
    && chmod +x /usr/local/bin/xidel \
    && rm -rf /tmp/xidel* \
    || echo "xidel install via sourceforge failed — installing from alternative" \
    && apt-get update && apt-get install -y --no-install-recommends fpc 2>/dev/null || true

# ─── Python dependencies ──────────────────────────────────────────
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r /tmp/requirements.txt

# ─── Playwright headless browser binaries ─────────────────────────
RUN playwright install --with-deps chromium \
    && playwright install-deps chromium

# ─── Working directory & scripts ──────────────────────────────────
WORKDIR /workspace

COPY scripts/ /opt/agentic-scripts/
RUN chmod +x /opt/agentic-scripts/* 2>/dev/null || true

ENV PATH="/opt/agentic-scripts:${PATH}"

# ─── Entrypoint ───────────────────────────────────────────────────
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["--help"]
