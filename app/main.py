from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import Base, engine
from app.models import post, user          # needed so that models are registered
from app.routers import auth, posts, comments


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown: dispose the engine
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)