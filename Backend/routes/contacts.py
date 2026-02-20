from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from Backend.helpers.contact_query import insert_contact
from Backend.helpers.contact_query import get_all_contacts
from Backend.helpers.user_query import get_user_from_db
from ..config.database import User
from ..helpers.authentication_helpers import get_current_user
from sqlalchemy import select
router = APIRouter(tags = ["Contacts"], prefix = "/contacts")




 
@router.post("/{username}/follow")
async def create_contact(username: str, current_user: User = Depends(get_current_user)):
    if username == current_user.username: 
        raise HTTPException(status_code= status.HTTP_403_FORBIDDEN,  detail = "Cant send contact req to your self")
    reciever = await get_user_from_db(username = username)
    if reciever is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,  detail = "{username} not found")
    res = await insert_contact(sender_id= current_user.id, reciever_id= reciever.id)

    if not res: raise HTTPException(status_code= status.HTTP_409_CONFLICT,  detail = "Contact Already exists")
    return JSONResponse(content=f"Now following {username}", status_code=status.HTTP_201_CREATED)




@router.get("/")
async def get_current_user_contacts(current_user: User = Depends(get_current_user)):
    res = await get_all_contacts(current_user.id)
    d_res = [{"id": user.id, "username": user.username, "name": user.name} for user in res]
    return d_res