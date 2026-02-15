import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from Backend.main import app
from Backend.helpers.authentication_helpers import create_access_token
import uuid

transport = ASGITransport(app=app)
BASE_URL = "http://test"


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as c:
        yield c


async def create_user(client):
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    await client.post("/auth/signup", json={
        "username": username,
        "name": "Test User",
        "password": "test123"
    })
    return username


def auth_as(client, username):
    token = create_access_token({"username": username, "name": "Test User"})
    client.cookies.set("access_token", token)


@pytest.mark.asyncio
async def test_send_message(client):
    user1 = await create_user(client)
    user2 = await create_user(client)
    auth_as(client, user1)

    msg = await client.post(f"/messages/{user2}", json={"content": "Hello"})
    assert msg.status_code == 201