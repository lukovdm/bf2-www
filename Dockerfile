# Use the official Python image from the Docker Hub
FROM python:3.11

# These two environment variables prevent __pycache__/ files.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.3.0 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_HOME=/root/.poetry
# Use production settings
ENV DJANGO_SETTINGS_MODULE website.settings.production
# Add poetry to PATH
ENV PATH="/root/.poetry/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential \
        # deps for postgress interaction
        postgresql-client

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /bf2-www

# Copy requirements
COPY pyproject.toml poetry.lock ./

# Install requirements for production
RUN poetry install --no-ansi --without dev --extras "production"

# Copy entrypoint
COPY config/entrypoint.sh ./

# Copy the rest of the code. 
COPY website ./

ENTRYPOINT ["./entrypoint.sh"]
