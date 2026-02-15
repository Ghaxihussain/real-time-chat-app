from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.responses import Content

from Backend.helpers.contact_query import insert_contact
from ..config.database import get_db, User, Contact, Message
from ..schemas.messages_schemas import SendMessage
from ..helpers.authentication_helpers import get_current_user
from ..helpers.user_query import get_user_from_db
from ..helpers.message_query import get_chat, insert_message

router = APIRouter(tags = ["messages"], prefix = "/messages")




@router.post("/{username}")
async def send_msg(username: str, message : SendMessage, current_user : User = Depends(get_current_user)):
    reciever = await get_user_from_db(username = username)
    if reciever is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"The {username} not found")
    await insert_contact(current_user.id, reciever.id) # insert the contact before sending the msg, so that we can have a record
    await insert_contact(reciever.id,current_user.id) # should be in both diorection, becouse of the receiver should also recieve the nsgs
    await insert_message(sender_id = current_user.id, receiver_id = reciever.id, content=message.content)
    return JSONResponse(content = "Message sent", status_code= 201)
    

@router.get("/{username}/conversation")
async def get_contact_chat(username: str, offset:int, limit: int, current_user: User = Depends(get_current_user)):
    reciever = await get_user_from_db(username = username)
    if reciever is None:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"The {username} not found")
    chat = [
    {
        "content" : msg.content,
        "sended" : msg.sender_id == current_user.id,
        "created_at" : msg.created_at
    } for msg in await get_chat(current_user.id, reciever.id)]


    return chat
