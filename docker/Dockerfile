# This Dockerfile is adapted from the great poetry multi-stage build example from here:
# https://github.com/michaeloliverx/python-poetry-docker-example/blob/master/docker/Dockerfile
FROM python:3.10-slim as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# builder-base is used to build dependencies
FROM python-base as builder-base
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        build-essential

# Install Poetry - respects $POETRY_VERSION & $POETRY_HOME
ENV POETRY_VERSION=1.1.7
RUN curl -sSL https://install.python-poetry.org | python3 -

# We copy our Python requirements here to cache them
# and install only runtime deps using poetry
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --no-dev


# 'development' stage installs all dev deps and can be used to develop code.
# For example using docker-compose to mount local volume under /app
FROM python-base as development
# Copying poetry and venv into image
COPY --from=builder-base $POETRY_HOME $POETRY_HOME
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

# Copying in our entrypoint
COPY ./docker/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# venv already has runtime deps installed we get a quicker install
WORKDIR $PYSETUP_PATH
RUN poetry install
WORKDIR /app
COPY . .

EXPOSE 8000
ENTRYPOINT /docker-entrypoint.sh $0 $@
CMD ["./manage.py", "runserver", "0.0.0.0:8000"]


FROM development AS test
RUN coverage run --rcfile ./pyproject.toml -m pytest ./tests
RUN coverage report --fail-under 95


FROM python-base as production
COPY --from=builder-base $VENV_PATH $VENV_PATH
COPY ./docker/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

COPY ./addresses_service /app/addresses_service
WORKDIR /app

ENTRYPOINT /docker-entrypoint.sh $0 $@
CMD ["gunicorn", "--bind", ":80", "addresses_service.wsgi:application"]