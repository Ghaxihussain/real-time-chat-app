from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import os
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
class Base(DeclarativeBase):
    pass

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    sender_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    read = Column(Boolean, default= False)



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)


class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    contact_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with async_session() as session:
        yield session
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


