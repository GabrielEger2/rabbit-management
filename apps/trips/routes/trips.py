from http import HTTPStatus
from fastapi import APIRouter, Query, Path, Depends
from common.schemas import Unauthorized

router = APIRouter()


@router.get(
    "/",
    status_code=HTTPStatus.OK,
    responses={401: {"model": Unauthorized}},
    summary="Retrieve Users",
    description="Retrieve a list of users with pagination and optional sorting.",
)
async def read_users(
):
    return await 42