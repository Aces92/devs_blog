from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.post import Post, Comment
from app.schemas.schemas import CommentCreate, CommentResponse
from app.utils.jwt import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["Comments"]
)


@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if post exists
    result = await db.execute(select(Post).where(Post.id == post_id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    new_comment = Comment(
        content=comment.content,
        owner_id=current_user.id,
        post_id=post_id
    )

    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)

    # Reload with owner
    result = await db.execute(
        select(Comment)
        .where(Comment.id == new_comment.id)
        .options(selectinload(Comment.owner))
    )
    return result.scalar_one()


@router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_all_comments(
    post_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Comment)
        .where(Comment.post_id == post_id)
        .options(selectinload(Comment.owner))
        .order_by(Comment.created_at.desc())
    )
    comments = result.scalars().all()

    if not comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No comments found for this post"
        )

    return comments


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    updated_comment: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Comment)
        .where(Comment.id == comment_id)
        .options(selectinload(Comment.owner))
    )
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if current_user.id != comment.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to update this comment"
        )

    comment.content = updated_comment.content

    await db.commit()
    await db.refresh(comment)

    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )

    if current_user.id != comment.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment"
        )

    await db.delete(comment)
    await db.commit()

    return {
        "message": "Comment successfully deleted"
    }

