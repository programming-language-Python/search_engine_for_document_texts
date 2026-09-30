from fastapi import HTTPException
from starlette import status

from db.config import settings
from repositories import ElasticsearchRepository
from schemas import DocumentSchema
from utils.repository import AbstractRepository


class DocumentService:
    """
    Бизнес-логика работы с документами.

    PostgreSQL остаётся источником истины: Elasticsearch используется
    только для определения релевантных id.
    """

    def __init__(
            self,
            document_repo: AbstractRepository,
            elasticsearch_repo: ElasticsearchRepository,
    ):
        """
        Принимает класс репозитория PostgreSQL и готовый репозиторий Elasticsearch.
        """
        self.document_repo: AbstractRepository = document_repo()
        self.elasticsearch_repo: ElasticsearchRepository = elasticsearch_repo

    async def search_documents(self, text: str) -> list[DocumentSchema]:
        """
        Возвращает до ES_DOCS_LIMIT документов по фразе, отсортированных
        по убыванию даты создания. Отвечает 503, если Elasticsearch недоступен.
        """
        if not (await self.elasticsearch_repo.is_available()):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Elasticsearch недоступен",
            )

        document_ids: list[int] = await self.elasticsearch_repo.search_ids(text)
        return await self.document_repo.find_by_ids(document_ids, limit=settings.ES_DOCS_LIMIT)

    async def reindex_all(self) -> int:
        """
        Пересоздаёт индекс Elasticsearch и загружает в него все документы
        из PostgreSQL пачками по ES_SCROLL_SIZE. Возвращает число проиндексированных записей.
        """
        if not (await self.elasticsearch_repo.is_available()):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Elasticsearch недоступен",
            )

        await self.elasticsearch_repo.create_index(recreate=True)
        indexed: int = 0
        page: int = 1

        while True:
            documents: list[DocumentSchema] = await self.document_repo.find_all(
                page=page,
                limit=settings.ES_SCROLL_SIZE,
            )

            if not documents:
                break

            indexed += await self.elasticsearch_repo.bulk_index(documents)

            if len(documents) < settings.ES_SCROLL_SIZE:
                break

            page += 1

        return indexed

    async def delete_document(self, document_id: int) -> int:
        """
        Удаляет документ из PostgreSQL, затем из Elasticsearch.
        """
        await self.document_repo.delete(document_id)
        await self.elasticsearch_repo.delete_document(document_id)
        return document_id
