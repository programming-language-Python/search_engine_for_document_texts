from repositories import DocumentRepository
from services import DocumentService


def document_service():
    return DocumentService(DocumentRepository)
