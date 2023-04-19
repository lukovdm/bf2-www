# Use the official Python image from the Docker Hub
FROM python:3.11

# These two environment variables prevent __pycache__/ files.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.4.0 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_HOME="/opt/poetry"
# Use production settings
ENV DJANGO_SETTINGS_MODULE website.settings.production
# Add poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

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
RUN poetry install --no-ansi --no-dev --extras "production"

# Copy entrypoint
COPY config/entrypoint.sh ./

# Copy the rest of the code. 
COPY website ./

# Compile scss to css
#RUN ./manage.py compilescss
#
## Collect all static files for serving
#RUN ./manage.py collectstatic --no-input

ENTRYPOINT ["./entrypoint.sh"]
