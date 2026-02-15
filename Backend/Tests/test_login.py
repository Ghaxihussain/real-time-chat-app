import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from Backend.main import app
import uuid

transport = ASGITransport(app=app)
BASE_URL = "http://test"


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as c:
        yield c


async def signup(client, username=None, name="Test User", password="test123"):
    username = username or f"testuser_{uuid.uuid4().hex[:8]}"
    res = await client.post("/auth/signup", json={
        "username": username,
        "name": name,
        "password": password
    })
    return res, username


@pytest.mark.asyncio
async def test_signup(client):
    res, _ = await signup(client)
    assert res.status_code == 201


@pytest.mark.asyncio
async def test_signup_duplicate(client):
    await signup(client, username="duplicate")
    res, _ = await signup(client, username="duplicate")
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_signin(client):
    await signup(client, username="loginuser")
    res = await client.post("/auth/signin", json={
        "username": "loginuser",
        "password": "test123"
    })
    assert res.status_code == 200
    assert "access_token" in res.cookies


@pytest.mark.asyncio
async def test_signin_wrong_password(client):
    await signup(client, username="wrongpwuser")
    res = await client.post("/auth/signin", json={
        "username": "wrongpwuser",
        "password": "wrongpassword"
    })
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_signin_nonexistent_user(client):
    res = await client.post("/auth/signin", json={
        "username": "nobody",
        "password": "test123"
    })
    assert res.status_code == 404