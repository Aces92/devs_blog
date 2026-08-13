from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.post import Post, Comment
from app.models.user import User
from app.schemas.schemas import CommentCreate, CommentResponse, PostResponse
from app.utils.jwt import get_current_user

router = APIRouter(
    prefix="/posts",
    tags=["Comments"]
)

#creating comments for a post 
@router.post("/{post_id}/comments", response_model=CommentResponse)
async def create_comment(
    post_id: int,
    comment: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    #querying the database for checking if the posts exists or not 
    post = db.query(Post).filter(Post.id == post_id).first() 

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
#Adding a new comment on the database 
    new_comment = Comment(
        content=comment.content,
        owner_id=current_user.id,
        post_id=post_id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment

#getting all comments from a post
@router.get("/{post_id}/comments", response_model=list[CommentResponse])
async def get_all(
    post_id: int,
    db: Session = Depends(get_db)
):
    #db query for all comments
    comments = db.query(Comment).filter(Comment.post_id == post_id).all() 

    if not comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comments not found"
        )

    return comments

#updating route for comments
@router.patch("/{update}", response_model=CommentResponse)
async def update_comment(comment_id: int, updated_comment: CommentCreate, db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):

    comments = db.query(Comment).filter(Comment.id == comment_id).first()  #database query for existing comment

    if not comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail= "comment not found"
        )

    if current_user.id != comments.owner_id: #ownership checks for comments
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not allowed"
        )
    comments.content = updated_comment.content  # updating comments

    db.commit()
    db.refresh(comments)

    return comments

#deleting route for comments
@router.delete("/{post_id}/comments/{comment_id}")
async def delete(id: int, current_user: User = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    
    comments = db.query(Comment).filter(Comment.id == id).first() #database query for existing comments

    if not comments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='comment not found'
        )

    if current_user.id  != comments.owner_id: #ownership checks
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST ,
            detail= " Not authorized"
            )

    db.delete(comments)
    db.commit()

    return {
        "message": "Comment successfully deleted"
    }














