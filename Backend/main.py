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



@app.on_event("startup")
async def startup():
    await init_db()
    async with async_session() as db:
        user1= User(username="ghazihussainn", name="ghazi", password=get_password_hash("123"))
        user2= User(username="syed", name="ghazi", password=get_password_hash("123"))

        db.add(user1)
        db.add(user2)
        await db.commit()