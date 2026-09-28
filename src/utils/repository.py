from abc import ABC, abstractmethod

from fastapi import HTTPException
from sqlalchemy import select
from starlette import status

from db.db import async_session_factory


class AbstractRepository(ABC):

    @abstractmethod
    async def find_all(self, text: str):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, document_id: int):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    model = None

    async def find_all(self, text: str):
        async with async_session_factory() as session:
            stmt = select(self.model)
            res = await session.execute(stmt)
            res = [row[0].to_read_model() for row in res.all()]
            return res

    async def delete(self, id_: int) -> dict:
        async with async_session_factory() as session:
            result = await session.execute(select(self.model).filter(self.model.id == id_))
            obj = result.scalars().first()

            if obj is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"{self.model.display_name} не найден")

            await session.delete(obj)
            await session.commit()

            return {"message": "Successfully deleted"}
