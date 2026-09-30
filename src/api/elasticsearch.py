from typing import Annotated

from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends

from api.dependencies import get_es_client

router = APIRouter(
    prefix="/elasticsearch",
    tags=["Elasticsearch"],
)


@router.get("/ping")
async def ping(es_client: Annotated[AsyncElasticsearch, Depends(get_es_client)]) -> dict:
    """
    Проверяет доступность Elasticsearch и возвращает состояние кластера.
    """
    is_alive: bool = await es_client.ping()

    if not is_alive:
        return {"status": "error", "message": "Elasticsearch недоступен"}

    health: dict = await es_client.cluster.health()
    return {
        "status": "success",
        "message": "Connected to Elasticsearch",
        "cluster_status": health["status"],
        "number_of_nodes": health["number_of_nodes"],
        "active_shards": health["active_shards"],
    }
