ARG PYTHON_VERSION=3.12-alpine

# Stage 1: Base image with Poetry
FROM python:${PYTHON_VERSION} as base-stage

# Install dependencies and poetry
ENV POETRY_HOME="/opt/poetry"
RUN apk add --no-cache curl gcc libc-dev libffi-dev
RUN curl -sSL https://install.python-poetry.org | python3 -

# Stage 2: Install Python dependencies
FROM base-stage as dependencies-stage

ENV PATH="$POETRY_HOME/bin:$PATH"

# Copy poetry requirement files
WORKDIR /app
ADD pyproject.toml poetry.lock /app/

# Install Python dependencies
RUN poetry config virtualenvs.in-project true # Make sure that the virtualenv is created in the project directory
RUN poetry install --no-ansi --only main,api --no-root

# Stage 3: Final image
FROM python:${PYTHON_VERSION}

# Copy the virtualenv from the dependencies stage
COPY --from=dependencies-stage /app/.venv /app/.venv

# Add required files
ADD ./src /app/src
ADD ./uvicorn_disable_logging.json /app/uvicorn_disable_logging.json
ADD ./alembic.ini /app/alembic.ini
ADD ./pyproject.toml /app/pyproject.toml
ADD ./docker/api/prestart.sh /app/prestart.sh
ADD ./docker/api/prestart.sh /app/prestart.sh
ADD ./docker/api/gunicorn_conf.py /app/gunicorn_conf.py
ADD ./docker/api/start.sh /app/start.sh

# Set the working directory
WORKDIR /app

# Set user and group
RUN addgroup -g 1000 app && \
    adduser --shell /sbin/nologin --disabled-password --no-create-home --uid 1000 --ingroup app app && \
    chown -R app:app /app && \
    chmod +x /app/prestart.sh /app/start.sh

USER app

# Export the port
EXPOSE 8000

ENV LOG_JSON_FORMAT=true
ENV PATH="/app/.venv/bin:$PATH"
ENV FASTAPI_ENV=production
ENV MODULE_NAME=src.backend.main

# Install code as a package
RUN pip install . --no-dependencies

CMD ["/app/start.sh"]
