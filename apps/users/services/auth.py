import bcrypt
import jwt
import datetime
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from common import get_db
from models import UserModel
from typing import Optional
from schemas import Token, AccessToken
from pydantic import EmailStr
from http import HTTPStatus
from sqlalchemy import select
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))


class AuthService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def authenticate_user(self, email: EmailStr, password: str) -> Token:
        user = await self._get_user_by_email(email)
        if not user or not self._verify_password(password, user.password):
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid email or password"
            )

        access_token = self._create_access_token(
            data={"id": user.id, "username": user.username}
        )
        refresh_token = self._create_refresh_token(
            data={"id": user.id, "username": user.username}
        )

        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    async def refresh_token(self, refresh_token: str) -> AccessToken:
        payload = self._decode_token(refresh_token)
        id: int = payload.get("id")

        user = await self._get_user_by_id(id)
        if not user:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="User not found"
            )

        access_token = self._create_access_token(data={"id": user.id})

        return AccessToken(access_token=access_token, token_type="bearer")

    async def logout(self, token: str) -> None:
        # skip for now
        print("Logout token:", token)
        pass

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def _create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def _create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.datetime.utcnow() + datetime.timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def _decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Invalid token"
            )

    async def _get_user_by_email(self, email: str) -> Optional[UserModel]:
        result = await self.db_session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalars().first()

    async def _get_user_by_id(self, user_id: int) -> Optional[UserModel]:
        result = await self.db_session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        return result.scalars().first()


def get_auth_service(db_session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db_session)
