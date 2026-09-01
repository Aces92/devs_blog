from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.user import User
from app.models.post import Post, Comment
from app.schemas.schemas import PostCreate, PostResponse, PostUpdate
from app.utils.jwt import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_post = Post(
        title=post.title,
        content=post.content,
        owner_id=current_user.id
    )

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    # Reload with owner
    result = await db.execute(
        select(Post)
        .where(Post.id == new_post.id)
        .options(selectinload(Post.owner))
    )
    return result.scalar_one()


@router.get("/", response_model=list[PostResponse])
async def get_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.owner))
        .offset(skip)
        .limit(limit)
        .order_by(Post.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{id}", response_model=PostResponse)
async def get_post(
    id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Post)
        .where(Post.id == id)
        .options(
            selectinload(Post.owner),
            selectinload(Post.comments).selectinload(Comment.owner)
        )
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    return post


@router.put("/{id}", response_model=PostResponse)
async def update_post(
    id: int,
    updated_post: PostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Post)
        .where(Post.id == id)
        .options(selectinload(Post.owner))
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if current_user.id != post.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )

    if updated_post.title is not None:
        post.title = updated_post.title
    if updated_post.content is not None:
        post.content = updated_post.content

    await db.commit()
    await db.refresh(post)

    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Post).where(Post.id == id))
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )

    if current_user.id != post.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )

    await db.delete(post)
    await db.commit()

    return {
        "message": "Comment successfully deleted"
    }