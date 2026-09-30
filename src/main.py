from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.routers import all_routers
from db.db import async_engine
from db.es import close_es_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управляет жизненным циклом приложения: после остановки освобождает
    соединение с Elasticsearch и пул соединений PostgreSQL.
    """
    yield
    await close_es_client()
    await async_engine.dispose()


app = FastAPI(
    title="Простой поисковик по текстам документов",
    lifespan=lifespan,
)

for router in all_routers:
    app.include_router(router)


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
