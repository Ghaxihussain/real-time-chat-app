from fastapi import WebSocket
from typing import List


class ChatManager():
    def __init__(self) -> None:
        self.active_con: dict[str, WebSocket] = {}

    async def connect(self, username, wb: WebSocket):
        await wb.accept()
        
        if username in self.active_con:
            try:
                await self.active_con[username].close()
            except:
                pass
        self.active_con[username] = wb

    async def disconnect(self, username):
        self.active_con.pop(username, None) 

    async def send_to_user(self, username, message: dict):
        ws = self.active_con.get(username)
        if ws:
            try:
                await ws.send_json(message)
            except:
                await self.disconnect(username)

    async def is_online(self, username):
        return username in self.active_con

    async def send_status(self, username: str, contact_ids: List[str], status: str):
        for id in contact_ids:
            ws = self.active_con.get(id)
            if ws:
                try:
                    await ws.send_json({
                        "type": "status_change",
                        "contact_id": username,
                        "status": status
                    })
                except:
                    await self.disconnect(id)

manager = ChatManager()