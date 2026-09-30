from elasticsearch import AsyncElasticsearch, NotFoundError

from db.config import settings
from db.es import INDEX_SETTINGS
from schemas import DocumentSchema


class ElasticsearchRepository:
    """
    Доступ к индексу Elasticsearch: создание индекса, полнотекстовый поиск,
    массовая индексация и удаление документов.
    """

    def __init__(self, es_client: AsyncElasticsearch, index: str | None = None):
        """
        Принимает асинхронный клиент и имя индекса (по умолчанию — из настроек).
        """
        self.es_client: AsyncElasticsearch = es_client
        self.index: str = index or settings.ES_INDEX

    async def is_available(self) -> bool:
        """
        Проверяет, отвечает ли Elasticsearch.
        """
        return bool(await self.es_client.ping())

    async def create_index(self, recreate: bool = False) -> bool:
        """
        Создаёт индекс с русским анализатором. Если recreate=True — сначала удаляет
        существующий индекс. Возвращает True, если индекс был создан.
        """
        if await self.es_client.indices.exists(index=self.index):
            if not recreate:
                return False

            await self.es_client.indices.delete(index=self.index)

        await self.es_client.indices.create(index=self.index, **INDEX_SETTINGS)
        return True

    async def search_ids(self, text: str) -> list[int]:
        """
        Выполняет match-запрос по полю text и возвращает id всех найденных документов.

        Индекс хранит только id и text, поэтому сортировать выдачу здесь нечем:
        порядок и ограничение применяет PostgreSQL. Документы вычитываются
        постранично через scroll, чтобы не потерять совпадения за пределами
        первой страницы. Поле _source не запрашивается, Elasticsearch не
        передаёт лишние данные.
        """
        response = await self.es_client.search(
            index=self.index,
            size=settings.ES_SCROLL_SIZE,
            scroll="1m",
            query={"match": {"text": {"query": text}}},
            source=False,
        )

        document_ids: list[int] = [int(hit["_id"]) for hit in response["hits"]["hits"]]
        scroll_id: str | None = response.get("_scroll_id")

        try:
            while scroll_id and len(response["hits"]["hits"]) == settings.ES_SCROLL_SIZE:
                response = await self.es_client.scroll(scroll_id=scroll_id, scroll="1m")
                document_ids.extend(int(hit["_id"]) for hit in response["hits"]["hits"])
                scroll_id = response.get("_scroll_id")
        finally:
            if scroll_id:
                await self.es_client.clear_scroll(scroll_id=scroll_id)

        return document_ids

    async def bulk_index(self, documents: list[DocumentSchema]) -> int:
        """
        Индексирует пачку документов одним bulk-запросом.

        В индекс попадают только id и text: остальные поля документа берутся
        из PostgreSQL по найденным id. id документа в Elasticsearch совпадает
        с id в PostgreSQL. Возвращает количество проиндексированных записей.
        """
        if not documents:
            return 0

        operations: list[dict] = []

        for document in documents:
            operations.append({"index": {"_index": self.index, "_id": document.id}})
            operations.append({"id": document.id, "text": document.text})

        response = await self.es_client.bulk(operations=operations, refresh=True)
        indexed: int = len(response["items"])
        failed: list[dict] = [item["index"] for item in response["items"] if item["index"].get("error")]

        if failed:
            raise RuntimeError(f"Не удалось проиндексировать {len(failed)} документов: {failed[0]}")

        return indexed

    async def index_document(self, document: DocumentSchema) -> None:
        """
        Индексирует один документ, перезаписывая существующую запись с тем же id.
        В индекс попадают только id и text.
        """
        await self.es_client.index(
            index=self.index,
            id=document.id,
            document={"id": document.id, "text": document.text},
            refresh=True,
        )

    async def delete_document(self, document_id: int) -> bool:
        """
        Удаляет документ из индекса по id. Возвращает False, если документа в индексе нет.
        """
        try:
            await self.es_client.delete(index=self.index, id=document_id, refresh=True)
            return True
        except NotFoundError:
            return False
