from datetime import datetime
from typing import Annotated

from sqlalchemy import text, MetaData, ARRAY, String
from sqlalchemy.orm import Mapped, mapped_column

from schemas import DocumentSchema
from db.db import Base

metadata_obj = MetaData()

intpk = Annotated[int, mapped_column(primary_key=True)]
created_date = Annotated[
    datetime,
    mapped_column(
        server_default=text("TIMEZONE('utc', now())"),
    ),
]


class Document(Base):
    """
    Документ в таблице document — источник истины для поисковой выдачи.
    """

    __tablename__ = "document"
    display_name = "Документ"

    id: Mapped[intpk]
    rubrics: Mapped[list[str]] = mapped_column(ARRAY(String))
    text: Mapped[str]
    created_date: Mapped[created_date]

    def to_read_model(self) -> DocumentSchema:
        """
        Преобразует ORM-объект в Pydantic-схему ответа API.
        """
        return DocumentSchema(
            id=self.id,
            rubrics=self.rubrics,
            text=self.text,
            created_date=self.created_date,
        )
