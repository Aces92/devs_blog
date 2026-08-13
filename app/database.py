from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") #getting the database url or connection from the environment vars

#creating a database engine
engine = create_engine(DATABASE_URL)

#creating a database session for each request
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

class Base(DeclarativeBase):
    pass

#a function that executes one db request at a time
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()