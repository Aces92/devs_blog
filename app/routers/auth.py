from fastapi  import APIRouter, HTTPException, status, Depends
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token, get_current_user
from app.schemas.schemas import UserCreate, UserResponse, UserLogin
from app.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

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
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    email_exists = db.query(User).filter(User.email == form_data.username).first()

    if not email_exists:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid username or password"
        )

    if not verify_password(
    form_data.password,
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

@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user