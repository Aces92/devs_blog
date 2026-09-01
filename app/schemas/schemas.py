from pydantic import BaseModel, EmailStr, ConfigDict, Field
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PostCreate(BaseModel):
    title: str = Field(
        min_length=5,
        max_length=100
    )
    content: str = Field(
        min_length=10,
        max_length=1000
    )


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    owner_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PostUpdate(BaseModel):
    title: str
    content: str


class CommentCreate(BaseModel):
    content: str = Field(
        min_length=1,
        max_length=500
    )


class UserPublic(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)


class CommentResponse(BaseModel):
    id: int
    content: str
    owner: UserPublic
    post_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)