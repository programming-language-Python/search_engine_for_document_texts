-- ============================================
-- Загрузка документов из CSV в PostgreSQL
--
-- Запускать именно через psql (используется \copy):
--   psql -U user -d documents -f load_documents.sql
--
-- Путь к CSV задан литералом в строке \copy ниже: psql не умеет
-- подставлять переменные в имя файла \copy. Чтобы сменить путь,
-- отредактируйте его или запустите скрипт в Docker (entrypoint
-- подставляет путь автоматически).
-- ============================================

-- ============================================
-- 1. Схема (совпадает с src/models/models.py)
-- ============================================
CREATE TABLE IF NOT EXISTS document (
    id           bigserial   PRIMARY KEY,
    rubrics      text[]      NOT NULL DEFAULT '{}',
    text         text        NOT NULL,
    created_date timestamptz NOT NULL DEFAULT timezone('utc', now())
);

-- сортировка выдачи: первые 20 по дате создания
CREATE INDEX IF NOT EXISTS ix_document_created_date ON document (created_date DESC);

-- ============================================
-- 2. Staging + загрузка CSV
-- ============================================
DROP TABLE IF EXISTS document_import;

CREATE UNLOGGED TABLE document_import (
    text         text,
    created_date text,
    rubrics      text
);

-- файл читает клиент (psql), поэтому путь указывается от машины, где запущен psql
\copy document_import (text, created_date, rubrics) FROM './data/posts.csv' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8');

-- ============================================
-- 3. Перенос в document
-- ============================================
TRUNCATE TABLE document;

INSERT INTO document (rubrics, text, created_date)
SELECT
    COALESCE(
        ARRAY(
            SELECT trim(item, chr(39)::text)                        -- 'VK-123' -> VK-123
            FROM unnest(
                     regexp_split_to_array(
                         translate(btrim(rubrics, '[]'), chr(39)::text, ''),
                         ',\s*'
                     )
                 ) AS item
            WHERE translate(btrim(rubrics, '[]'), chr(39)::text, '') <> ''  -- '[]' -> пустой массив
        ),
        '{}'
    )::text[],
    text,
    created_date::timestamp AT TIME ZONE 'UTC'                      -- CSV без TZ, считаем UTC
FROM document_import
WHERE text IS NOT NULL;

DROP TABLE document_import;

-- ============================================
-- 4. Проверка
-- ============================================
SELECT count(*) AS documents,
       min(created_date) AS first,
       max(created_date) AS last
FROM document;
