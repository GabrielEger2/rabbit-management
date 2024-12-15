from http import HTTPStatus
from fastapi import APIRouter, Depends
from schemas import UserLogin, Token, TokenRefresh, Logout, AccessToken
from services import AuthService, get_auth_service

router = APIRouter()


@router.post(
    "/login",
    status_code=HTTPStatus.OK,
    response_model=Token,
    summary="Login User",
    description="Authenticate user and generate a JWT token.",
)
async def login(user_in: UserLogin, service: AuthService = Depends(get_auth_service)):
    return await service.authenticate_user(user_in.email, user_in.password)


@router.post(
    "/refresh",
    status_code=HTTPStatus.OK,
    response_model=AccessToken,
    summary="Refresh Token",
    description="Refresh the JWT token using a refresh token.",
)
async def refresh_token(
    token_in: TokenRefresh, service: AuthService = Depends(get_auth_service)
):
    return await service.refresh_token(token_in.refresh_token)


@router.post(
    "/logout",
    status_code=HTTPStatus.NO_CONTENT,
    summary="Logout User",
    description="Invalidate the user's JWT token.",
)
async def logout(logout_in: Logout, service: AuthService = Depends(get_auth_service)):
    await service.logout(logout_in.token)
