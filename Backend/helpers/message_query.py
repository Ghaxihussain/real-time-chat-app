from fastapi import status, HTTPException
from fastapi.responses import JSONResponse
from ..config.database import async_session
from sqlalchemy import select, insert
from ..config.database import Message


async def insert_message(sender_id, receiver_id, content):
    try:
        async with async_session() as session:
            await session.execute(insert(Message).values(content=content, sender_id=sender_id, receiver_id =receiver_id))
            await session.commit()
        return JSONResponse(status_code=status.HTTP_201_CREATED, content="Created")
    except Exception as e:
        print(f"INSERT ERROR: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to insert message")