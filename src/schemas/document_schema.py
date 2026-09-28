from datetime import datetime

from pydantic import BaseModel


class DocumentSchema(BaseModel):
    id: int
    rubrics: list[str]
    text: str
    created_date: datetime
