from httpx import AsyncClient, ASGITransport
from Backend.main import app
from Backend.helpers.authentication_helpers import create_access_token
import uuid
import pytest_asyncio




transport = ASGITransport(app=app)
BASE_URL = "http://test"


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as c:
        yield c




def auth_as(client, username):
    token = create_access_token({"username": username, "name": "Test User"})
    client.cookies.set("access_token", token)




async def create_user(client):
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    await client.post("/auth/signup", json={
        "username": username,
        "name": "Test User",
        "password": "test123"
    })
    return username
