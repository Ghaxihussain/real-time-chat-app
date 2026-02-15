from fastapi import WebSocket



class ChatManager():
    def __init__(self) -> None:
        self.acive_connetions: dict[int, WebSocket] = {}
    

    async def connect(self, user_id, wb: WebSocket):
        await wb.accept()
        self.acive_connetions[user_id] = wb

    

    async def disconnect(self, user_id):
        self.acive_connetions.pop(user_id)


    async def send_to_user(self, user_id, message: dict):
        ws = self.acive_connetions.get(user_id)
        if ws:
            await ws.send_json(message)


manager = ChatManager()