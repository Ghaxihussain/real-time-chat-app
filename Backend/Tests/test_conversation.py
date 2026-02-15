from .helpers import auth_as, client, create_user
import pytest




@pytest.mark.asyncio
async def test_get_conversation(client):
    user1 = await create_user(client)
    user2 = await create_user(client)
    auth_as(client, user1)

    await client.post(f"/messages/{user2}", json={"content": "Hello"})
    await client.post(f"/messages/{user2}", json={"content": "How are you?"})

    res = await client.get(f"/messages/{user2}/conversation?offset=0&limit=20")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert data[0]["content"] == "Hello"
    assert data[1]["content"] == "How are you?"
    assert data[0]["sended"] == True


@pytest.mark.asyncio
async def test_get_conversation_both_sides(client):
    user1 = await create_user(client)
    user2 = await create_user(client)

    auth_as(client, user1)
    await client.post(f"/messages/{user2}", json={"content": "Hey"})

    auth_as(client, user2)
    await client.post(f"/messages/{user1}", json={"content": "Hi back"})

    res = await client.get(f"/messages/{user1}/conversation?offset=0&limit=20")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert data[0]["sended"] == False
    assert data[1]["sended"] == True


@pytest.mark.asyncio
async def test_get_conversation_empty(client):
    user1 = await create_user(client)
    user2 = await create_user(client)
    auth_as(client, user1)

    res = await client.get(f"/messages/{user2}/conversation?offset=0&limit=20")
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
async def test_get_conversation_unknown_user(client):
    user1 = await create_user(client)
    auth_as(client, user1)

    res = await client.get(f"/messages/nobody/conversation?offset=0&limit=20")
    assert res.status_code == 404