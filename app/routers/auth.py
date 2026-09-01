from fastapi import APIRouter, HTTPException, status, Depends
from app.utils.security import hash_password, verify_password
from app.utils.jwt import create_access_token, get_current_user
from app.schemas.schemas import UserCreate, UserResponse
from app.database import get_db
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
async def user_registration(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    email_result = await db.execute(
        select(User).where(User.email == user.email)
    )

    email_exists = email_result.scalar_one_or_none()

    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="email already exists"
        )

    username_result = await db.execute(
        select(User).where(User.username == user.username)
    )

    username_exists = username_result.scalar_one_or_none()

    if username_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="username already exists"
        )

    hashed_password = hash_password(user.password)

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    email_result = await db.execute(
        select(User).where(User.email == form_data.username)
    )

    email_exists = email_result.scalar_one_or_none()

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