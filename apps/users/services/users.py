import bcrypt
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from schemas import UsersPublic, UserPublic, UserUpdate
from common import get_db
from models import UserModel
from http import HTTPStatus
from common import get_total_count, paginate_query


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_users(
        self, page: int, order: str, sort: str, username: Optional[str]
    ) -> UsersPublic:
        query = self._build_user_query(order, sort, username)
        total_count = await get_total_count(self.db_session, query)
        users = await paginate_query(self.db_session, query, page, 25)

        users_public = [UserPublic.from_orm(user) for user in users]
        total_pages = (total_count + 25 - 1) // 25

        return UsersPublic(data=users_public, page=page, total_pages=total_pages)

    async def create_user(self, user: UserModel) -> UserModel:
        existing_user = await self._get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST, detail="User already exists"
            )

        hashed_password = self._hash_password(user.password)
        db_user = UserModel(
            username=user.username,
            email=user.email,
            password=hashed_password,
            level=user.level,
        )

        self.db_session.add(db_user)
        await self.db_session.commit()
        await self.db_session.refresh(db_user)
        return db_user

    async def update_user(self, user_id: int, user_update: UserUpdate) -> UserModel:
        db_user = await self._get_user_by_id(user_id)

        if not db_user:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="User not found"
            )

        update_data = user_update.dict(exclude_unset=True)

        if "email" in update_data and update_data["email"] != db_user.email:
            existing_user = await self._get_user_by_email(update_data["email"])
            if existing_user:
                raise HTTPException(
                    status_code=HTTPStatus.CONFLICT, detail="Email already in use"
                )

        if "password" in update_data:
            update_data["password"] = self._hash_password(update_data["password"])

        for key, value in update_data.items():
            setattr(db_user, key, value)

        await self.db_session.commit()
        await self.db_session.refresh(db_user)
        return db_user

    async def delete_user(self, user_id: int) -> None:
        db_user = await self._get_user_by_id(user_id)

        if not db_user:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="User not found"
            )

        await self.db_session.delete(db_user)
        await self.db_session.commit()

    def _hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    async def _get_user_by_email(self, email: str) -> Optional[UserModel]:
        result = await self.db_session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalars().first()

    async def _get_user_by_id(self, user_id: int) -> Optional[UserModel]:
        return await self.db_session.get(UserModel, user_id)

    def _build_user_query(self, order: str, sort: str, username: Optional[str]):
        query = select(UserModel)
        if username:
            query = query.where(UserModel.username.ilike(f"%{username}%"))

        sort_field = {
            "username": UserModel.username,
            "joined": UserModel.joined,
            "level": UserModel.level,
        }.get(sort, UserModel.username)

        if order == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

        return query


def get_user_service(db_session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db_session)
