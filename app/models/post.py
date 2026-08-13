from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
if TYPE_CHECKING:
    from app.models.user import User

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(String(1000))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    owner: Mapped["User"] = relationship("User", back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post")


class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    content: Mapped[str] = mapped_column(String(500))
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    owner: Mapped["User"] = relationship("User",back_populates="comments")
    post: Mapped["Post"] = relationship("Post", back_populates="comments")