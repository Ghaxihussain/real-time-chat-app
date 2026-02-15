import pytest
from .helpers import create_user, auth_as, client




@pytest.mark.asyncio
async def test_send_message(client):
    user1 = await create_user(client)
    user2 = await create_user(client)
    auth_as(client, user1)

    msg = await client.post(f"/messages/{user2}", json={"content": "Hello"})
    assert msg.status_code == 201