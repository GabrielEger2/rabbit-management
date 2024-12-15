from typing import List
from pydantic import EmailStr
from sqlmodel import Field, SQLModel
import datetime
from typing import Optional


class UserBase(SQLModel):
    username: str = Field(index=True, max_length=50)
    email: EmailStr = Field(unique=True, index=True, max_length=250)
    level: int = Field(default=1)


class UserPublic(UserBase):
    id: int
    joined: datetime.datetime
    is_active: bool = Field(default=True)


class UsersPublic(SQLModel):
    data: List[UserPublic]
    page: int
    total_pages: int


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=100)


class UserUpdate(SQLModel):
    username: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None, max_length=250)
    is_active: Optional[bool] = Field(None)
    level: Optional[int] = Field(None)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
