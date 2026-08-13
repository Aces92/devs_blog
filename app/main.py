from fastapi import FastAPI
from app.database import Base,engine
from app.models import post, user
from app.routers import auth, posts, comments



Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)

