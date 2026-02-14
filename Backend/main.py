from fastapi import FastAPI
from .routes import login, contacts, users
from .config.database import init_db
app = FastAPI()

app.include_router(login.router)
app.include_router(contacts.router)
app.include_router(users.router)



@app.on_event("startup")
async def startup():
    await init_db()