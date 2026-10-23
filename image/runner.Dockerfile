FROM python:3.12.11-slim-bullseye

# Bullseye has moved to the Debian archive, including its security packages.
RUN printf '%s\n' \
    'deb https://archive.debian.org/debian bullseye main' \
    'deb https://archive.debian.org/debian-security bullseye-security main' \
    > /etc/apt/sources.list \
    && apt-get -o Acquire::Check-Valid-Until=false update \
    && apt-get install -y --no-install-recommends \
    build-essential ca-certificates curl git libffi-dev libssl-dev libpq-dev \
    libxml2-dev libxslt1-dev libjpeg-dev libfreetype6-dev libtiff-dev libzip-dev \
    libpcre2-dev libmagic1 poppler-utils ghostscript fonts-noto-cjk \
    fonts-noto-color-emoji default-jre-headless unzip \
    && rm -rf /var/lib/apt/lists/*
RUN python -m pip install --no-cache-dir \
    'pip==24.1.2' 'tox==3.28.0' 'tox-setuptools-version==0.0.0.3'
COPY scripts/install_dependencies.py scripts/prepare.py /opt/weko-ci/
WORKDIR /code
CMD ["sleep", "infinity"]
