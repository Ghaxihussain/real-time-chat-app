# tests/test_auth.py
import pytest
from httpx import AsyncClient, ASGITransport
from Backend.main import app
import uuid
transport = ASGITransport(app=app)
BASE_URL = "http://test"



@pytest.mark.asyncio
async def test_signup():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        response = await client.post("/auth/signup", json={
            "username": f"testuser_{uuid.uuid4().hex[:8]}",
            "name": "Test User",
            "password": "test123"
        })
        assert response.status_code == 201

@pytest.mark.asyncio
async def test_signup_duplicate():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        await client.post("/auth/signup", json={
            "username": "duplicate",
            "name": "Dup User",
            "password": "test123"
        })
        response = await client.post("/auth/signup", json={
            "username": "duplicate",
            "name": "Dup User",
            "password": "test123"
        })
        assert response.status_code == 409

@pytest.mark.asyncio
async def test_signin():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        await client.post("/auth/signup", json={
            "username": "loginuser",
            "name": "Login User",
            "password": "test123"
        })
        response = await client.post("/auth/signin", json={
            "username": "loginuser",
            "password": "test123"
        })
        assert response.status_code == 200
        assert "access_token" in response.cookies

@pytest.mark.asyncio
async def test_signin_wrong_password():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        response = await client.post("/auth/signin", json={
            "username": "loginuser",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

@pytest.mark.asyncio
async def test_signin_nonexistent_user():
    async with AsyncClient(transport=transport, base_url=BASE_URL) as client:
        response = await client.post("/auth/signin", json={
            "username": "nobody",
            "password": "test123"
        })
        assert response.status_code == 404