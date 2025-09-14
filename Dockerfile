FROM python:3.13-bookworm AS base
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*
RUN groupadd -r appuser && useradd -r -g appuser appuser
FROM base AS builder

COPY --from=ghcr.io/astral-sh/uv:0.4 /uv /bin/uv
RUN chmod +x /bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_CACHE_DIR=/tmp/uv-cache
RUN mkdir -p $UV_CACHE_DIR && chown -R appuser:appuser $UV_CACHE_DIR
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN  uv sync --frozen
COPY  . .
RUN  uv export --format=requirements-txt --no-dev > requirements.txt
RUN chmod +x ./entrypoint.sh

FROM base AS production
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY --from=builder /etc/passwd /etc/passwd
COPY --from=builder /etc/group /etc/group
COPY --from=builder /bin/uv /bin/uv
COPY --from=builder  /app/src/ /app/src/
COPY --from=builder  /app/requirements.txt /app/
COPY --from=builder  /app/entrypoint.sh /app/
RUN  uv pip install --system -r requirements.txt
RUN rm -rf /tmp/uv-cache && \
    find /usr/local -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
ENTRYPOINT ["./entrypoint.sh"]