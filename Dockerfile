FROM python:3.12-slim AS base

FROM base AS builder
COPY --from=ghcr.io/astral-sh/uv:0.4 /uv /bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app
COPY . /app/
RUN uv sync
RUN uv export --format=requirements-txt > requirements.txt
RUN chmod +x ./entrypoint.sh

FROM base AS runtime

WORKDIR /app
COPY --from=builder /app/src/ /app/
COPY --from=builder /app/requirements.txt /app/

RUN pip3 install -r requirements.txt
ENTRYPOINT [ "./entrypoint.sh" ]
