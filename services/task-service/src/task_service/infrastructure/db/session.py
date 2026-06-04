import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from collections.abc import AsyncGenerator

load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL is None:
    raise RuntimeError("DATABASE_URL is not set")

async_engine = create_async_engine(DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

async def get_db()-> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session