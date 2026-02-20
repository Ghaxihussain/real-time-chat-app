from fastapi import Depends, WebSocket, WebSocketDisconnect, APIRouter
from ..helpers.contact_query import get_contact_python_list
from Backend.config.database import User
from ..helpers.web_socket_manager import manager
from ..helpers.authentication_helpers import verify_access_token
import asyncio
router = APIRouter(prefix="/ws")


@router.websocket("/")
async def ws_endpoint(wb: WebSocket):
    token = wb.cookies.get("access_token")
    if not token:
        await wb.close(code=1008)
        return

    try:
        user = verify_access_token(token)
    except:
        await wb.close(code=1008)
        return

    await manager.connect(user["username"], wb)
    contact_username= await get_contact_python_list(user["id"])

    print(f"[WS] User {user['username']} connected, contacts: {contact_username}") 
    await manager.send_status(user["username"], contact_username, status="online")
    print("Hellow", manager.active_con)
    await asyncio.sleep(2)

    for contact_username in contact_username:
        if contact_username in manager.active_con:
            await wb.send_json({
                "type": "status_change",
                "contact_id": contact_username,
                "status": "online"
            })
    try:
        while True:
            await wb.receive_json()

    except WebSocketDisconnect:
        await asyncio.sleep(1)

        if manager.active_con.get(user["username"]) == wb:
            await manager.send_status(user["username"], contact_username, status="offline")
            await manager.disconnect(user["username"])
            print("Disconnected", manager.active_con)
        else:
            print("Skipped disconnect")