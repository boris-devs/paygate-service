from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import get_db
from src.repositories.users import UserRepository
from src.services.users_service import UsersService
from src.schemas.auth import UserLoginRequestSchema, UserLoginTokenResponseSchema

router = APIRouter()


def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
	return UserRepository(session)


def get_user_service(user_repo: UserRepository = Depends(get_user_repository)) -> UsersService:
	return UsersService(user_repo)


@router.post("/login", response_model=UserLoginTokenResponseSchema)
async def login(
		payload: UserLoginRequestSchema,
		user_service: UsersService = Depends(get_user_service)
):
	return await user_service.login_user(payload)
