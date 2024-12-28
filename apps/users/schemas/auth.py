from pydantic import EmailStr, BaseModel
from sqlmodel import Field, SQLModel


class AccessToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class Token(AccessToken):
    pass


class UserLogin(SQLModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)


class Logout(BaseModel):
    token: str
