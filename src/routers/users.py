from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_db

from src.repositories.users import UserRepository
from src.services.billing_service import BillingService
from src.models.users import User
from src.schemas.users import UserProfileSchema
from src.schemas.billings import PaymentsResponseSchema, AccountsResponseSchema
from src.repositories.billing import BillingRepository
from src.services.users_service import UsersService
from src.security.utils import get_current_user

router = APIRouter(prefix="/me")


def get_user_service(db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    return UsersService(user_repo)


def get_billing_service(db: AsyncSession = Depends(get_db)):
    billing_repo = BillingRepository(db)
    user_repo = UserRepository(db)
    return BillingService(billing_repo, user_repo)


@router.get("/", response_model=UserProfileSchema)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/accounts/", response_model=List[AccountsResponseSchema])
async def get_my_accounts(
    current_user: User = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
):
    return await billing_service.get_user_accounts(user_id=current_user.id)


@router.get("/payments/", response_model=List[PaymentsResponseSchema])
async def get_my_payments(
    current_user: User = Depends(get_current_user),
    billing_service: BillingService = Depends(get_billing_service),
):
    return await billing_service.get_user_payments(user_id=current_user.id)
