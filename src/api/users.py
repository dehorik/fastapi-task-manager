from typing import Annotated

from fastapi import APIRouter, Depends, status

from schemas import UserSchema, UserSchemaCreate
from services import UsersService
from .dependencies import get_users_service


router = APIRouter(prefix="/users")


@router.post("", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(
        user: UserSchemaCreate,
        users_service: Annotated[UsersService, Depends(get_users_service)]
):
    user = await users_service.create_user(user)
    return user
