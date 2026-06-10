from typing import List
from fastapi import HTTPException, status
from sqlalchemy.orm import selectinload

from src.repositories.users import UserRepository
from src.security.passwords import hash_password
from src.models.users import User
from src.schemas.admin import (
    UserCreateSchema,
    UserUpdateSchema,
    AdminUserResponseSchema,
)


class AdminService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_users_list(self) -> List[AdminUserResponseSchema]:
        """
        Get all users along with their accounts and balances.
        """
        users = await self.user_repo.get_all_with_accounts()
        return [AdminUserResponseSchema.model_validate(user) for user in users]

    async def create_user(self, payload: UserCreateSchema) -> AdminUserResponseSchema:
        """
        Create a new user. Validates email uniqueness.
        """
        existing_user = await self.user_repo.get_by_email(payload.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )

        hashed_password = hash_password(payload.password)
        new_user = User(
            email=payload.email,
            password_hash=hashed_password,
            full_name=payload.full_name,
            role=payload.role,
        )

        await self.user_repo.create(new_user)
        await self.user_repo.session.commit()

        await self.user_repo.session.refresh(new_user)

        user_data = {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name,
            "role": new_user.role,
            "accounts": []
        }

        return AdminUserResponseSchema.model_validate(user_data)

    async def update_user(
        self, user_id: int, payload: UserUpdateSchema
    ) -> AdminUserResponseSchema:
        """
        Update user data. Re-hashes password if provided.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        update_data = payload.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            update_data["password_hash"] = hash_password(update_data["password"])
            del update_data["password"]

        if "email" in update_data and update_data["email"] != user.email:
            existing_email = await self.user_repo.get_by_email(update_data["email"])
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This email is already taken by another user",
                )

        await self.user_repo.update(user_id, update_data)
        await self.user_repo.session.commit()

        return AdminUserResponseSchema.model_validate(
            await self.user_repo.get_by_id(user_id)
        )

    async def delete_user(self, user_id: int) -> dict:
        """
        Delete user by ID.
        """
        success = await self.user_repo.delete(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        await self.user_repo.session.commit()
        return {
            "status": "success",
            "detail": f"User {user_id} has been successfully deleted",
        }
