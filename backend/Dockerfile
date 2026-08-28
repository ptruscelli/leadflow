FROM python:3.13-slim-bookworm

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


ENV PYTHONDONTWRITEBYTECODE=1 \
    # unbuffered stdout, so api logs are printed immediately (incl. magic_link fallback)
    PYTHONUNBUFFERED=1 \
    # link mode copy, so the uv package is copied to the container
    UV_LINK_MODE=copy \
    # compile bytecode, so the api is faster
    UV_COMPILE_BYTECODE=1 \
    # synced venv is first, so CMD can execute uv directly (without 'uv run' each time)
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# create a non-root user
RUN useradd --create-home --uid 1000 appuser

COPY pyproject.toml uv.lock ./

# no pytest for prod build
# fail build if uv.lock is not up to date
RUN uv sync --locked --no-dev 

COPY . .

# so named volume is writable by the user after USER appuser
RUN mkdir -p /app/data && chown appuser:appuser /app/data

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]