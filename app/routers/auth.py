from fastapi  import APIRouter, HTTPException, status, Depends
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.schemas.schemas import UserCreate, UserResponse, UserLogin
from app.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post('/register',  response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def user_registration(user: UserCreate, db: Session = Depends(get_db)):
    
    email_exists = db.query(User).filter(User.email == user.email).first()
    
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_400_CONFLICT,
            detail="email already exists"
        )
    
    username_exists = db.query(User).filter(User.username == user.username).first()

    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_400_CONFLICT,
            detail="username already exists"
        )

    hashed_password = hash_password(user.password)
    new_user = User(
    username=user.username,
    email=user.email,
    hashed_password=hashed_password
)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    email_exists = db.query(User).filter(User.email == user.email).first()

    if not email_exists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid username or password"
        )
    print(email_exists.hashed_password)
    print(type(email_exists.hashed_password))
    if not verify_password(
    user.password,
    email_exists.hashed_password
):
     raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="invalid username or password"
    )
    access_token = create_access_token(
        data={"user_id": email_exists.id}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }