from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from ..helpers.user_query import get_user_from_db
from ..helpers.authentication_helpers import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from ..config.database import get_db
router = APIRouter(tags = ["Delete user"], prefix = "/users")




@router.delete("/")
async def delete_user(current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    current_user.is_deleted = True
    current_user.name = "Deleted User"
    current_user.password = ""
    await db.commit()
    return JSONResponse(content="User deleted", status_code=200)


