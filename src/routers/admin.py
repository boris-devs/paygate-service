from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import get_db
from src.repositories.users import UserRepository
from src.services.admin_service import AdminService
from src.schemas.admin import UserCreateSchema, UserUpdateSchema, AdminUserResponseSchema
from src.security.utils import get_current_admin

router = APIRouter()


def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
	return UserRepository(session)


def get_admin_service(user_repo: UserRepository = Depends(get_user_repository)) -> AdminService:
	return AdminService(user_repo)


@router.get(
	"/users/",
	response_model=List[AdminUserResponseSchema],
	dependencies=[Depends(get_current_admin)]
)
async def list_users(admin_service: AdminService = Depends(get_admin_service)):
	return await admin_service.get_users_list()


@router.post(
	"/users/",
	response_model=AdminUserResponseSchema,
	status_code=status.HTTP_201_CREATED,
	dependencies=[Depends(get_current_admin)]
)
async def create_user(
		payload: UserCreateSchema,
		admin_service: AdminService = Depends(get_admin_service)
):
	return await admin_service.create_user(payload)


@router.patch(
	"/users/{user_id}/",
	response_model=AdminUserResponseSchema,
	dependencies=[Depends(get_current_admin)]
)
async def update_user(
		user_id: int,
		payload: UserUpdateSchema,
		admin_service: AdminService = Depends(get_admin_service)
):
	return await admin_service.update_user(user_id, payload)


@router.delete(
	"/users/{user_id}/",
	dependencies=[Depends(get_current_admin)]
)
async def delete_user(
		user_id: int,
		admin_service: AdminService = Depends(get_admin_service)
):
	return await admin_service.delete_user(user_id)
