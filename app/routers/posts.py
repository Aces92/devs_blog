from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.post import Post
from app.schemas.schemas import PostCreate, PostResponse, PostUpdate
from app.utils.jwt import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.post("/", response_model=PostResponse)
async def create_posts(post:PostCreate, db: Session = Depends(get_db),
current_user:User = Depends(get_current_user)):

    new_post = Post (title=post.title, content=post.content,
                owner_id = current_user.id)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/", response_model=list[PostResponse])
async def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    
    return posts


@router.get("/{id}", response_model=PostResponse)
async def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "Not Found"
        )

    return post

@router.put("/{id}", response_model=PostResponse)
async def update_post(id:int, updated_post : PostCreate, db: Session = Depends(get_db),
                      current_user : User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == id).first()
    if not post:
         raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail="Not Found"
    )
    if current_user.id != post.owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail= " FORBIDDEN "
        )
    post.title = updated_post.title
    post.content = updated_post.content

    db.commit()
    db.refresh(post)

    return post

@router.delete("/{id}")
async def delete_post(id: int, db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    post = db.query(Post).filter(Post.id == id).first()

    if not post:
       raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail="Not Found"
    )

    if current_user.id != post.owner_id:
      raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not authorized"
    )

    db.delete(post)
    db.commit()

    return {
    "message": "Post deleted successfully."
}