FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app/src"

WORKDIR /app

RUN pip install --upgrade pip \
    && pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-root --no-interaction --no-ansi

COPY ./src ./src
COPY ./migrations ./migrations
COPY ./alembic.ini ./alembic.ini

EXPOSE 8000

CMD ["python", "./src/run.py"]