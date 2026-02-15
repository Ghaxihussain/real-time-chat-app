import pytest
from httpx import AsyncClient, ASGITransport
from Backend.main import app
from Backend.helpers.authentication_helpers import create_access_token
import uuid
import pytest_asyncio
from .helpers import client, create_user, auth_as



@pytest.mark.asyncio
async def test_contact(client):
    user1 = await create_user(client)
    user2 = await create_user(client)
    auth_as(client, user1)

    res = await client.post(f"/contacts/{user2}/follow")
    assert res.status_code == 201


@pytest.mark.asyncio
async def test_duplicate_contact(client):
    user1 = await create_user(client)
    user2 = await create_user(client)
    auth_as(client, user1)

    await client.post(f"/contacts/{user2}/follow")
    res = await client.post(f"/contacts/{user2}/follow")
    assert res.status_code == 409


@pytest.mark.asyncio
async def test_self_contact(client):
    user1 = await create_user(client)
    auth_as(client, user1)

    res = await client.post(f"/contacts/{user1}/follow")
    assert res.status_code == 201


@pytest.mark.asyncio
async def test_unknown_contact(client):
    user1 = await create_user(client)
    auth_as(client, user1)

    res = await client.post(f"/contacts/unknown/follow")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_get_contacts(client):
    user1 = await create_user(client)
    user2 = await create_user(client)
    user3 = await create_user(client)
    auth_as(client, user1)

    await client.post(f"/contacts/{user2}/follow")
    await client.post(f"/contacts/{user3}/follow")

    res = await client.get("/contacts/")
    data = res.json()
    assert len(data) == 2
    usernames = [c["username"] for c in data]
    assert user2 in usernames
    assert user3 in usernames