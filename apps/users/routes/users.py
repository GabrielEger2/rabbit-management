from http import HTTPStatus
from fastapi import APIRouter, Query, Path, Depends
from schemas import UsersPublic, UserPublic, UserCreate, UserUpdate
from common import Unauthorized
from typing import Optional
from services import UserService, get_user_service

router = APIRouter()


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    response_model=UsersPublic,
    responses={401: {"model": Unauthorized}},
    summary="Retrieve Users",
    description="Retrieve a list of users with pagination and optional sorting.",
)
async def read_users(
    page: Optional[int] = Query(
        ...,
        ge=1,
        description="Page number, must be greater than or equal to 1",
        missing=1,
    ),
    order: Optional[str] = Query(
        None,
        regex="^(asc|desc)$",
        description="Order type: [asc, desc], default is ascending",
    ),
    sort: Optional[str] = Query(
        None,
        regex="^(username|joined|level)$",
        description="Sort type: [username, joined, level], default is username",
    ),
    username: Optional[str] = Query(None, description="Filter by username"),
    service: UserService = Depends(get_user_service),
):
    return await service.get_users(page, order, sort, username)


@router.post(
    "/",
    status_code=HTTPStatus.CREATED,
    response_model=UserPublic,
    responses={401: {"model": Unauthorized}},
    summary="Create User",
    description="Creates a new user, must have a unique email.",
)
async def create_user(
    user_in: UserCreate, service: UserService = Depends(get_user_service)
):
    return await service.create_user(user_in)


@router.put(
    "/{user_id}",
    status_code=HTTPStatus.OK,
    response_model=UserPublic,
    responses={401: {"model": Unauthorized}},
    summary="Update User",
    description="Updates a user.",
)
async def update_user(
    user_update: UserUpdate,
    user_id: int = Path(..., ge=1, description="ID of the user to update"),
    service: UserService = Depends(get_user_service),
):
    return await service.update_user(user_id, user_update)


@router.delete(
    "/{user_id}",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Delete User",
    responses={401: {"model": Unauthorized}},
    description="Deletes a user.",
)
async def delete_user(
    user_id: int = Path(..., ge=1, description="ID of the user to delete"),
    service: UserService = Depends(get_user_service),
):
    await service.delete_user(user_id)
