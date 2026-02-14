from pydantic import BaseModel




class Signup(BaseModel):
    username: str 
    password: str 
    name: str



class SignIn(BaseModel):
    username: str
    password: str


