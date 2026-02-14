from fastapi import FastAPI
from .routes import login
from .config.database import init_db
app = FastAPI()

app.include_router(login.router)




@app.on_event("startup")
async def startup():
    await init_db()