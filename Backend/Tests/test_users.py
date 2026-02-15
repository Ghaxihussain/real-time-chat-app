import pytest
from Backend.helpers.user_query import get_user_from_db
from .helpers import create_user, auth_as, client



@pytest.mark.asyncio
async def test_delete_user(client):
    username = await create_user(client)
    auth_as(client, username)

    del_req = await client.delete("/users/")
    assert del_req.status_code == 200

    res = await get_user_from_db(username=username)
    assert res.name == "Deleted User"
    assert res.is_deleted == True