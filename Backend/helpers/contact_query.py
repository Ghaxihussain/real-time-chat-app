from fastapi import HTTPException, status
from sqlalchemy import select, insert 
from ..config.database import Contact, async_session


async def get_contact(sender, reciever):
    async with async_session() as session:
        result = await session.execute(select(Contact).where(Contact.user_id == sender, Contact.contact_id == reciever))
        res1 = result.scalar_one_or_none()
    return res1


async def insert_contact(sender_id, reciever_id):
    res = await get_contact(sender=sender_id, reciever=reciever_id)
    if res is not None:
        return False

    try:
        async with async_session() as session:
            await session.execute(insert(Contact).values(user_id=sender_id, contact_id=reciever_id))
            await session.commit()
        return True
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Failed to insert contact")