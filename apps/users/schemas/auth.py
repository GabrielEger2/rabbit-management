from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class AccessToken(SQLModel):
    access_token: str
    token_type: str = "bearer"


class Token(AccessToken):
    refresh_token: str


class UserLogin(SQLModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class TokenRefresh(SQLModel):
    refresh_token: str


class Logout(SQLModel):
    token: str
