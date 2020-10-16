# Use the official Python image from the Docker Hub
FROM python:3.8

# These two environment variables prevent __pycache__/ files.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.1.3 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_PATH=/poetry
# Use production settings
ENV DJANGO_SETTINGS_MODULE giphousewebsite.settings.production
# Add poetry to PATH
ENV PATH="$POETRY_PATH/bin:$PATH"

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential

# install poetry - respects $POETRY_VERSION & $POETRY_HOME
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python
RUN mv /root/.poetry $POETRY_PATH

WORKDIR /bf2-www

# Copy requirements
COPY pyproject.toml poetry.lock ./

# Install requirements
RUN poetry install --no-dev

# Copy entrypoint
COPY entrypoint.sh ./

# Copy the rest of the code. 
COPY website ./

ENTRYPOINT ["./entrypoint.sh"]
