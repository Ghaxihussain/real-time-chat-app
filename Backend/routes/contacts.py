from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from ..config.database import Contact, User, get_db
from sqlalchemy.ext.asyncio import AsyncSession
from ..helpers.authentication_helpers import get_current_user
from sqlalchemy import select
router = APIRouter(tags = ["Contacts"], prefix = "/contacts")




 
@router.post("/{username}/follow")
async def follow_user(username: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):

    result = await db.execute(select(User).where(User.username == username))
    target_user = result.scalar_one_or_none()
    print(current_user)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{username} does not exist")
    
    if target_user.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot follow yourself")
    
    result1 = await db.execute(
        select(Contact).where(Contact.user_id == current_user.id, Contact.contact_id == target_user.id))

    result2 = await db.execute(
        select(Contact).where(Contact.user_id == target_user.id, Contact.contact_id == current_user.id))

    if result1.scalar_one_or_none() or result2.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Already following {username}")
    
    new_contact = Contact(user_id=current_user.id, contact_id=target_user.id)
    db.add(new_contact)
    await db.commit()  
    
    return JSONResponse(content=f"Now following {username}", status_code=status.HTTP_201_CREATED)