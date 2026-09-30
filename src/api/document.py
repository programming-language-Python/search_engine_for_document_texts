from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from api.dependencies import document_service
from schemas import DocumentSchema
from services import DocumentService

router = APIRouter(
    prefix="/document",
    tags=["Document"],
)


@router.get("", response_model=list[DocumentSchema])
async def search_documents(
        text: Annotated[str, Query(description="Фраза для поиска")],
        document_service: Annotated[DocumentService, Depends(document_service)],
) -> list[DocumentSchema]:
    """
    Ищет документы по произвольной фразе.

    Elasticsearch определяет релевантные id, после чего полные записи
    считываются из PostgreSQL и возвращаются в порядке выдачи —
    по убыванию даты создания.
    """
    return await document_service.search_documents(text)


@router.post("/reindex")
async def reindex_documents(
        document_service: Annotated[DocumentService, Depends(document_service)],
) -> dict:
    """
    Пересоздаёт индекс Elasticsearch и заново загружает в него
    все документы из PostgreSQL.
    """
    indexed: int = await document_service.reindex_all()
    return {"indexed": indexed}


@router.delete("/{document_id}")
async def delete_document(
        document_id: int,
        document_service: Annotated[DocumentService, Depends(document_service)],
) -> dict:
    """
    Удаляет документ по id одновременно из PostgreSQL и Elasticsearch.

    Возвращает 404, если документа нет в базе.
    """
    deleted_id: int = await document_service.delete_document(document_id)
    return {"document_id": deleted_id, "message": "Successfully deleted"}
