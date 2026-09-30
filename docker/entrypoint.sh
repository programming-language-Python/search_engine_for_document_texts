#!/bin/sh
set -e

CSV_PATH="${CSV_PATH:-/app/data/posts.csv}"
LOAD_SQL="/app/load_documents.sql"
API_URL="http://localhost:8000"

echo "[entrypoint] ждём PostgreSQL на ${DB_HOST}:${DB_PORT}..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" >/dev/null 2>&1; do
    sleep 2
done
echo "[entrypoint] PostgreSQL готов"

echo "[entrypoint] ждём Elasticsearch на ${ES_HOST}:${ES_PORT}..."
until curl -fs "http://${ES_HOST}:${ES_PORT}/_cluster/health" >/dev/null 2>&1; do
    sleep 2
done
echo "[entrypoint] Elasticsearch готов"

PG_URL="postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
DOCS_COUNT=$(psql "$PG_URL" -tAc "SELECT count(*) FROM document" 2>/dev/null || echo 0)

if [ "$DOCS_COUNT" = "0" ]; then
    echo "[entrypoint] база пуста, загружаем данные из ${CSV_PATH}"
    # \copy не принимает переменные psql, поэтому подменяем путь в тексте скрипта
    sed "s|FROM '[^']*'|FROM '${CSV_PATH}'|g" "$LOAD_SQL" > /tmp/load_documents.sql
    psql "$PG_URL" -v ON_ERROR_STOP=1 -f /tmp/load_documents.sql
else
    echo "[entrypoint] в базе уже ${DOCS_COUNT} документов, загрузка CSV пропущена"
fi

cd /app/src

echo "[entrypoint] запуск API"
uvicorn main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

trap 'kill -TERM "$API_PID" 2>/dev/null' TERM INT

echo "[entrypoint] ждём готовности API"
until curl -fs "${API_URL}/elasticsearch/ping" >/dev/null 2>&1; do
    if ! kill -0 "$API_PID" 2>/dev/null; then
        echo "[entrypoint] API не удалось запустить"
        exit 1
    fi
    sleep 2
done
echo "[entrypoint] API готов"

echo "[entrypoint] переиндексация в Elasticsearch"
curl -fs -X POST "${API_URL}/document/reindex"
echo ""

echo "[entrypoint] всё запущено: ${API_URL}/docs"
wait "$API_PID"
