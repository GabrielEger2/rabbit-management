from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def read_users():
    """Returns all users"""
    return {"message": "Welcome to the Users Section!"}
