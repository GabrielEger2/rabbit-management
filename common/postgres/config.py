import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from .registry import table_registry
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session
        await session.commit()


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)
