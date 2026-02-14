from pydantic import BaseModel



class DeleteIn(BaseModel):
    username: str
    password: str
