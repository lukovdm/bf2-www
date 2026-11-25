# Use the official Python image from the Docker Hub
FROM python:3.13

# Install uv, see https://docs.astral.sh/uv/guides/integration/docker/
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /bin/

# These environment variables prevent __pycache__/ files and make uv install
# into the project virtualenv at /bf2-www/.venv
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/bf2-www/.venv
# Use production settings
ENV DJANGO_SETTINGS_MODULE website.settings.production

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for building python deps
        build-essential \
        # deps for postgress interaction
        postgresql-client

WORKDIR /bf2-www

# Copy requirements
COPY pyproject.toml uv.lock ./

# Install requirements for production
RUN uv sync --locked --no-dev --extra production

# Copy entrypoint
COPY config/entrypoint.sh ./

# Copy the rest of the code.
COPY website ./

ENTRYPOINT ["./entrypoint.sh"]
