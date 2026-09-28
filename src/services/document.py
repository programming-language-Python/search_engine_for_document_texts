from utils.repository import AbstractRepository


class DocumentService:
    def __init__(self, document_repo: AbstractRepository):
        self.document_repo: AbstractRepository = document_repo()

    async def get_documents(self, text: str):
        documents = await self.document_repo.find_all(text)
        return documents

    async def delete_document(self, document_id: int) -> int:
        document_id = await self.document_repo.delete(document_id)
        return document_id
