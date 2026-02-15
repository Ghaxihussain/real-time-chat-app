from fastapi import FastAPI
from .routes import login, contacts, users, messages, ws
from fastapi.middleware.cors import CORSMiddleware
from .config.database import init_db
from fastapi.staticfiles import StaticFiles
from .helpers.authentication_helpers import get_password_hash
from .config.database import async_session, User
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="Frontend/static-test1"), name="static") ##
app.include_router(login.router)
app.include_router(contacts.router)
app.include_router(users.router)
app.include_router(messages.router)
app.include_router(ws.router)



@app.on_event("startup")
async def startup():
    await init_db()
    async with async_session() as db:
        user1= User(username="ghazihussainn", name="ghazi", password=get_password_hash("123"))
        user2= User(username="syed", name="ghazi", password=get_password_hash("123"))

        db.add(user1)
        db.add(user2)
        await db.commit()