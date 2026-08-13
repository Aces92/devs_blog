from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
if TYPE_CHECKING:
    from app.models.post import Post, Comment



class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username:Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(50), unique=True)
    hashed_password: Mapped[str] =mapped_column(String(255))
    created_at:Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    posts: Mapped[list["Post"]] = relationship("Post",back_populates="owner")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="owner")

