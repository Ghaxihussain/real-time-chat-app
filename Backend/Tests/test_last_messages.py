import pytest
from .helpers import create_user, client, auth_as



@pytest.mark.asyncio
async def test_get_conversations(client):
    user1 = await create_user(client)
    user2 = await create_user(client)
    user3 = await create_user(client)
    auth_as(client, user1)

    # Send messages to two different users
    await client.post(f"/messages/{user2}", json={"content": "Hey user2"})
    await client.post(f"/messages/{user3}", json={"content": "Hey user3"})
    await client.post(f"/messages/{user2}", json={"content": "Bye user2"})

    res = await client.get("/messages/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2

    # Last message to user2 should be "Bye user2" (most recent)
    user2_convo = next(c for c in data if c["username"] == user2)
    assert user2_convo["last_message"] == "Bye user2"

    user3_convo = next(c for c in data if c["username"] == user3)
    assert user3_convo["last_message"] == "Hey user3"


@pytest.mark.asyncio
async def test_get_conversations_empty(client):
    user1 = await create_user(client)
    auth_as(client, user1)

    res = await client.get("/messages/")
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
async def test_get_conversations_both_directions(client):
    user1 = await create_user(client)
    user2 = await create_user(client)

    auth_as(client, user1)
    await client.post(f"/messages/{user2}", json={"content": "Hello"})

    auth_as(client, user2)
    await client.post(f"/messages/{user1}", json={"content": "Hi back"})

    auth_as(client, user1)
    res = await client.get("/messages/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["last_message"] == "Hi back"