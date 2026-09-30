from abc import ABC, abstractmethod

from fastapi import HTTPException
from sqlalchemy import select
from starlette import status

from db.db import async_session_factory
from schemas import DocumentSchema


class AbstractRepository(ABC):
    """
    Контракт репозитория документов: чтение, пагинация и удаление.
    """

    @abstractmethod
    async def find_by_ids(self, ids: list[int], limit: int) -> list[DocumentSchema]:
        """
        Возвращает не более limit документов по списку id, отсортированных
        по убыванию даты создания.
        """
        raise NotImplementedError

    @abstractmethod
    async def find_all(self, page: int, limit: int) -> list[DocumentSchema]:
        """
        Возвращает страницу документов.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete(self, document_id: int) -> None:
        """
        Удаляет документ по id.
        """
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    """
    Реализация репозитория поверх асинхронного SQLAlchemy.
    model указывается в подклассе.
    """

    model = None

    async def find_by_ids(self, ids: list[int], limit: int) -> list[DocumentSchema]:
        """
        Забирает документы по id одним запросом IN (...), сортирует по убыванию
        даты создания и оставляет не более limit записей.

        Сортировка выполняется здесь, а не в Elasticsearch: индекс хранит
        только id и text, поэтому created_date в нём отсутствует.
        """
        if not ids:
            return []

        async with async_session_factory() as session:
            stmt = (
                select(self.model)
                .where(self.model.id.in_(ids))
                .order_by(self.model.created_date.desc())
                .order_by(self.model.id)
                .limit(limit)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [DocumentSchema.model_validate(document) for document in rows]

    async def find_all(self, page: int = 1, limit: int = 20) -> list[DocumentSchema]:
        """
        Возвращает страницу документов, отсортированных по убыванию даты создания.
        """
        if page < 1 or limit < 1:
            raise ValueError("page и limit должны быть положительными")
        async with async_session_factory() as session:
            stmt = (
                select(self.model)
                .order_by(self.model.created_date.desc())
                .order_by(self.model.id)
                .offset((page - 1) * limit)
                .limit(limit)
            )
            rows = (await session.execute(stmt)).scalars().all()
            return [DocumentSchema.model_validate(document) for document in rows]

    async def delete(self, document_id: int) -> None:
        """
        Удаляет документ по id. Отвечает 404, если документа нет в базе.
        """
        async with async_session_factory() as session:
            document = await session.get(self.model, document_id)

            if document is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.model.display_name} не найден",
                )

            await session.delete(document)
            await session.commit()
