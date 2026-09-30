from elasticsearch import AsyncElasticsearch

from db.config import settings

es_client = AsyncElasticsearch(
    hosts=[settings.ELASTICSEARCH_URL],
    request_timeout=30,
)

INDEX_SETTINGS = {
    "settings": {
        "analysis": {
            "filter": {
                "ru_stopwords": {"type": "stop", "stopwords": "_russian_"},
                "ru_stemmer": {"type": "stemmer", "language": "russian"},
            },
            "analyzer": {
                "ru_index": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "ru_stopwords", "ru_stemmer"],
                },
                "ru_search": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "ru_stopwords", "ru_stemmer"],
                },
            },
        },
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "id": {"type": "integer"},
            "text": {
                "type": "text",
                "analyzer": "ru_index",
                "search_analyzer": "ru_search",
            },
        }
    },
}


async def get_es_client() -> AsyncElasticsearch:
    """
    Возвращает общий клиент Elasticsearch.
    """
    return es_client


async def close_es_client() -> None:
    """
    Закрывает сессию клиента Elasticsearch при остановке приложения.
    """
    await es_client.close()
