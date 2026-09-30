import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "text",
    [
        "админ",
        "бы найти себе друга/подругу😄\"",
        "Админ лучший!)\nИщу девушку 15-16"
    ],
)
@pytest.mark.asyncio
async def test_count_limit_documents_1(text, test_client: AsyncClient):
    response = await test_client.get("/document", params={"text": text})
    count_documents = len(response.json())
    assert 20 >= count_documents > 0


@pytest.mark.asyncio
async def test_delete_no_existing_document(test_client: AsyncClient):
    response = await test_client.delete("/document/1000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_existing_document(test_client: AsyncClient):
    response = await test_client.delete("/document/1588")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_ping(test_client: AsyncClient):
    response = await test_client.get("/elasticsearch/ping")
    assert response.status_code == 200
