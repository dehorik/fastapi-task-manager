FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/fastapi_task_manager/src"

WORKDIR /fastapi_task_manager

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
  && poetry install --no-root --no-interaction --no-ansi

COPY . .

EXPOSE 80

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]