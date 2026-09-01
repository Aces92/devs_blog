from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import  DeclarativeBase
from dotenv import load_dotenv

import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") #getting the database url or connection from the environment vars

#creating a database engine
engine = create_async_engine(DATABASE_URL)

#creating a database session for each request
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

class Base(DeclarativeBase):
    pass

#a function that executes one db request at a time
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session