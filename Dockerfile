FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY pyproject.toml ./pyproject.toml
COPY alembic.ini ./alembic.ini
COPY src ./src
COPY data ./data
COPY load_documents.sql ./load_documents.sql
COPY docker/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && chmod +x /entrypoint.sh

FROM base AS app

WORKDIR /app/src

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=60s --retries=10 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/elasticsearch/ping', timeout=4).status == 200 else 1)"

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS tests

RUN pip install "pytest>=9.0.0,<10.0.0" "pytest-asyncio>=1.0.0,<2.0.0" "httpx>=0.28.0,<1.0.0"

COPY tests ./tests

WORKDIR /app

ENTRYPOINT ["python", "-m", "pytest"]
