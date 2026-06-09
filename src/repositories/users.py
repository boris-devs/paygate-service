from typing import Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.users import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(User).where(User.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    # ----ADMIN_METHODS----
    async def create(self, user: User) -> User:
        self.session.add(user)

        await self.session.flush()
        return user

    async def update(self, user_id: int, update_data: dict) -> Optional[User]:
        query = (
            update(User).where(User.id == user_id).values(**update_data).returning(User)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, user_id: int) -> bool:
        query = delete(User).where(User.id == user_id).returning(User.id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_all_with_accounts(self) -> List[User]:
        query = select(User).options(selectinload(User.accounts))
        result = await self.session.execute(query)
        return list(result.scalars().all())
