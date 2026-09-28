from typing import Annotated

from fastapi import APIRouter, Depends

from api import document_service
from services import DocumentService

router = APIRouter(
    prefix="/document",
    tags=["Document"],
)


@router.get("")
async def get_documents(
        document_service: Annotated[DocumentService, Depends(document_service)],
        text: str
):
    documents = await document_service.get_documents(text)
    return documents


@router.delete("")
async def delete_document(
        document_service: Annotated[DocumentService, Depends(document_service)],
        document_id: int
) -> dict:
    document_id = await document_service.delete_document(document_id)
    return {"document_id": document_id}
