from pydantic import BaseModel



class SendMessage(BaseModel):
    content: str