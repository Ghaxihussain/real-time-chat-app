from fastapi import FastAPI
from .routes import login, contacts, users, messages, ws
from fastapi.middleware.cors import CORSMiddleware
from .config.database import init_db
from fastapi.staticfiles import StaticFiles
from .helpers.authentication_helpers import get_password_hash
from .config.database import async_session, User
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = (
            "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net"
        )
        return response

app = FastAPI()
app.add_middleware(CSPMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:7000", "http://localhost:7000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="Frontend/Test_website"), name="static") ##
##
app.include_router(login.router)
app.include_router(contacts.router)
app.include_router(users.router)
app.include_router(messages.router)
app.include_router(ws.router)



from .config.database import async_session, User, Contact, Message  # make sure Contact & Message are imported

@app.on_event("startup")
async def startup():
    await init_db()
    async with async_session() as db:
       
        user1 = User(username="ghazihussainn", name="Ghazi Hussein", password=get_password_hash("123"))
        user2 = User(username="syed",          name="Syed Ali",      password=get_password_hash("123"))
        user3 = User(username="sara",           name="Sara Khan",     password=get_password_hash("123"))
        user4 = User(username="bilal",          name="Bilal Ahmed",   password=get_password_hash("123"))

        db.add_all([user1, user2, user3, user4])
        await db.flush()  

      
        contacts = [
            Contact(user_id=user1.id, contact_id=user2.id),
            Contact(user_id=user2.id, contact_id=user1.id),
            Contact(user_id=user1.id, contact_id=user3.id),
            Contact(user_id=user3.id, contact_id=user1.id),
            Contact(user_id=user1.id, contact_id=user4.id),
            Contact(user_id=user4.id, contact_id=user1.id),
        ]
        db.add_all(contacts)
        await db.flush()
        await db.commit()