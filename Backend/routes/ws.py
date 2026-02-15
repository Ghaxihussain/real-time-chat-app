from fastapi import Depends, WebSocket, WebSocketDisconnect, APIRouter

from Backend.config.database import User
from ..helpers.web_socket_manager import manager
from ..helpers.authentication_helpers import verify_access_token

router = APIRouter(prefix="/ws")


@router.websocket("/")
async def ws_endppoint(wb: WebSocket):
    token = wb.cookies.get("access_token")
    if not token:
        await wb.close(code=1008)  # Unauthorized
        return

    try:
        user = verify_access_token(token)
    except:
        await wb.close(code=1008)
        return 
    await manager.connect(user["id"], wb)
    try:
        while True:
            await wb.receive_json()

    except WebSocketDisconnect:
        await manager.disconnect(user["id"])

