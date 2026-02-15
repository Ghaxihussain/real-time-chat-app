import pytest
from httpx import AsyncClient, ASGITransport
from Backend.main import app  
from Backend.helpers.authentication_helpers import create_access_token
import uuid
transport = ASGITransport(app = app)
BASE_URL = "http://test"


# basic follow test — two fresh users, user1 follows user2, should work fine
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

        add_contact = await client.post(f"/contacts/{user2_username}/follow")
        
        assert add_contact.status_code == 201


# duplicate follow test — user1 tries to follow user2 twice, second attempt should be rejected with 409
@pytest.mark.asyncio
async def test_duplicate_contact():
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

        contect_first = await client.post(f"/contacts/{user2_username}/follow")
        contact_second = await client.post(f"/contacts/{user2_username}/follow")
        
        assert contact_second.status_code == 409


# self follow test — user tries to follow themselves, should be blocked with 400
@pytest.mark.asyncio
async def test_self_contact():
    async with AsyncClient(transport=transport, base_url = BASE_URL) as client:
        
        user1_username = f"testuser_{uuid.uuid4().hex[:8]}"

        user1 = await client.post("/auth/signup", json={
            "username": user1_username,
            "name": "Test User",
            "password": "test123"
        })

        TOKEN = create_access_token({"username": user1_username, "name": "Test User"})
        client.cookies.set("access_token", TOKEN)

        add_contact = await client.post(f"/contacts/{user1_username}/follow")
        
        assert add_contact.status_code == 201


# unknown user test — trying to follow someone who doesnt exist, should return 404
@pytest.mark.asyncio
async def test_unknown_contact():
    async with AsyncClient(transport=transport, base_url = BASE_URL) as client:
        
        user1_username = f"testuser_{uuid.uuid4().hex[:8]}"

        user1 = await client.post("/auth/signup", json={
            "username": user1_username,
            "name": "Test User",
            "password": "test123"
        })

        TOKEN = create_access_token({"username": user1_username, "name": "Test User"})
        client.cookies.set("access_token", TOKEN)

        add_contact = await client.post(f"/contacts/unknown/follow")
        
        assert add_contact.status_code == 404