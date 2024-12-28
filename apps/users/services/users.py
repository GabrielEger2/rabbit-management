import bcrypt
import json
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from schemas import UsersPublic, UserPublic, UserUpdate
from common.postgres import get_db
from common.redis import redis_client
from models import UserModel
from http import HTTPStatus
from common.postgres import get_total_count, paginate_query
from common.redis import (
    cache_with_expiry,
    cache_with_sliding_expiry,
    invalidate_cache,
    invalidate_pattern_cache,
)


class UserService:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get_users(
        self, page: int, order: str, sort: str, username: Optional[str]
    ) -> UsersPublic:
        cache_key = (
            f"users:page={page}:order={order}:sort={sort}:username={username or 'all'}"
        )

        async def fetch_users():
            query = self._build_user_query(order, sort, username)
            users = await paginate_query(self.db_session, query, page, 26)
            users_public = [UserPublic.from_orm(user) for user in users]

            next_page = None

            if len(users_public) > 25:
                next_page = page + 1
                users_public = users_public[:25]

            return {
                "data": [user.dict() for user in users_public],
                "page": page,
                "next": next_page,
            }

        cached_result = await cache_with_expiry(cache_key, fetch_users, ttl=300)

        return UsersPublic(
            data=[UserPublic(**user) for user in cached_result["data"]],
            page=cached_result["page"],
            next=cached_result.get("next"),
        )

    async def get_user(self, user_id: int) -> UserPublic:
        cache_key = f"user:details:{user_id}"

        async def fetch_user():
            db_user = await self._get_user_by_id(user_id)
            if not db_user:
                raise HTTPException(
                    status_code=HTTPStatus.NOT_FOUND, detail="User not found"
                )
            return UserPublic.from_orm(db_user).dict()

        cached_user = await cache_with_sliding_expiry(cache_key, fetch_user, ttl=300)
        return UserPublic(**cached_user)

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

        await invalidate_pattern_cache("users:*")
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

        await invalidate_cache(f"user:details:{user_id}")
        await invalidate_pattern_cache("users:*")
        return db_user

    async def delete_user(self, user_id: int) -> None:
        db_user = await self._get_user_by_id(user_id)

        if not db_user:
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="User not found"
            )

        await self.db_session.delete(db_user)
        await self.db_session.commit()

        await invalidate_cache(f"user:details:{user_id}")
        await invalidate_pattern_cache("users:*")

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
