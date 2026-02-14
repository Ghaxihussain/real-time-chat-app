import pytest
from httpx import AsyncClient, ASGITransport
from Backend.main import app
import uuid
from ..helpers.authentication_helpers import create_access_token
from ..helpers.user_query import get_user_from_db
transport = ASGITransport(app=app)
BASE_URL = "http://test"



@pytest.mark.asyncio
async def test_delete_user():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        username = f"testuser_{uuid.uuid4().hex[:8]}"
        user = await client.post("/auth/signup", json={
            "username": username,
            "name": "Test User",
            "password": "test123"
        })
        TOKEN = create_access_token({"username": username, "name": "Test User"})
        client.cookies.set("access_token", TOKEN)
        del_req = await client.delete("/users/")
        res = await get_user_from_db(username = username)
        assert del_req.status_code == 200
        assert res.name == "Deleted User"
        assert res.is_deleted == True