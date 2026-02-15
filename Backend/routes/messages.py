from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.responses import Content
from ..config.database import get_db, User, Contact, Message
from ..schemas.messages_schemas import SendMessage
from ..helpers.authentication_helpers import get_current_user
from ..helpers.user_query import get_user_from_db
from ..helpers.message_query import insert_message

router = APIRouter(tags = ["messages"], prefix = "/messages")




@router.post("/{username}")
async def send_msg(username: str, message : SendMessage, current_user : User = Depends(get_current_user)):
    reciever = await get_user_from_db(username = username)
    if reciever is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"The {username} not found")
    await insert_message(sender_id = current_user.id, receiver_id = reciever.id, content=message.content)
    return JSONResponse(content = "Message sent", status_code= 201)
    
