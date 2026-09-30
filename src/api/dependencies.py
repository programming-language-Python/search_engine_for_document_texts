from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.es import es_client
from repositories import DocumentRepository, ElasticsearchRepository
from services import DocumentService


def get_es_client() -> AsyncElasticsearch:
    """
    Возвращает общий асинхронный клиент Elasticsearch.
    """
    return es_client


def document_service(
    es_client: AsyncElasticsearch = Depends(get_es_client),
) -> DocumentService:
    """
    Собирает сервис документов из репозитория PostgreSQL и репозитория Elasticsearch.
    """
    return DocumentService(DocumentRepository, ElasticsearchRepository(es_client))
