from _pytest._code.code import TracebackStyle
from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from ..config.database import User, async_session
from sqlalchemy import select, insert, join, or_
from ..config.database import Message
from ..config.database import Contact

async def insert_message(sender_id, receiver_id, content):
    try:
        async with async_session() as session:
            await session.execute(insert(Message).values(content=content, sender_id=sender_id, receiver_id =receiver_id))
            await session.commit()
        return JSONResponse(status_code=status.HTTP_201_CREATED, content="Created")
    except Exception as e:
        print(f"INSERT ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to insert message")




async def get_all_contacts(user_id):
    async with async_session() as session:
        subquery = select(Contact.contact_id).where(Contact.user_id == user_id).subquery()
        result = await session.execute(select(User).where(User.id.in_(select(subquery.c.contact_id))))
        contacts = result.scalars().all()
    return contacts


async def get_chat(sender_id, receiver_id, offset=0, limit=20):
    async with async_session() as session:
        result = await session.execute(select(Message).where(or_(
        (Message.sender_id == sender_id) & (Message.receiver_id == receiver_id),
        (Message.sender_id == receiver_id) & (Message.receiver_id == sender_id),)
        )
        .order_by(Message.created_at)
        .offset(offset)
        .limit(limit)
        )
    return result.scalars().all()
        