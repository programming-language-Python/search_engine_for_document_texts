from datetime import datetime
from typing import Annotated

from sqlalchemy import text, MetaData, ARRAY, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.db import Base

metadata_obj = MetaData()

intpk = Annotated[int, mapped_column(primary_key=True)]
created_date = Annotated[datetime, mapped_column(
    server_default=text("TIMEZONE('utc', now())"),
)]



class Document(Base):
    __tablename__ = "document"
    display_name = "Документ"

    id: Mapped[intpk]
    rubrics: Mapped[list[str]] = mapped_column(ARRAY(String))
    text: Mapped[str]
    created_date: Mapped[created_date]
