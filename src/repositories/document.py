from models.models import Document
from utils.repository import SQLAlchemyRepository


class DocumentRepository(SQLAlchemyRepository):
    model = Document
