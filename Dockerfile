FROM python:3.11-slim

RUN pip install --no-cache-dir uv && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    libjpeg-dev \
    libopenblas-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN uv pip install --system -r requirements.txt

COPY app/ .

RUN useradd -m -u 1000 appuser && \
    mkdir -p /var/log/app /tmp/images && \
    chown -R appuser:appuser /app /var/log/app /tmp/images && \
    chmod 755 /var/log/app /tmp/images

USER appuser

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV MPLBACKEND=Agg

CMD ["python", "main.py"]
