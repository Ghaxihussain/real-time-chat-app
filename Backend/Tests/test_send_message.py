import pytest
from httpx import ASGITransport, AsyncClient
from Backend.main import app
from ..helpers.authentication_helpers import create_access_token
import uuid
transport = ASGITransport(app = app)
BASE_URL = "http://test"


@pytest.mark.asyncio
async def test_contact():
    async with AsyncClient(transport=transport, base_url = BASE_URL) as client:
        user1_username = f"testuser_{uuid.uuid4().hex[:8]}"
        user2_username = f"testuser_{uuid.uuid4().hex[:8]}"

        user1 = await client.post("/auth/signup", json={
            "username": user1_username,
            "name": "Test User",
            "password": "test123"
        })
       
        user2 = await client.post("/auth/signup", json={
            "username": user2_username,
            "name": "Test User",
            "password": "test123"
        })

        TOKEN = create_access_token({"username": user1_username, "name": "Test User"})
        client.cookies.set("access_token", TOKEN)

        msg = await client.post(f"/messages/{user2_username}", json= {"content": "Hello"})
        assert msg.status_code == 201
