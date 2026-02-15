from sqlalchemy import select, delete
from ..config.database import async_session, User





async def get_user_from_db(username = None, name = None, id = None):
    res = None
    if username is None and name is None and id is None:
        return None

    if username is not None:
        async with async_session() as session:
            res = await session.execute(select(User).where(User.username == username))
        return res.scalar_one_or_none()

    if name is not None:
        async with async_session() as session:
            res = await session.execute(select(User).where(User.name == name))
        return res.scalar_one_or_none()

    if id is not None:
        async with async_session() as session:
            res = await session.execute(select(User).where(User.id == id))
        return res.scalar_one_or_none()
      