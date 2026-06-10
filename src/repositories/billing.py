from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.billing import Account, Payment


class BillingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_accounts(self, user_id: int) -> List[Account]:
        query = select(Account).where(Account.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_user_payments(self, user_id: int) -> List[Payment]:
        query = (
            select(Payment)
            .join(Account)
            .where(Account.user_id == user_id)
            .order_by(Payment.created_at.desc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_payment_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        query = select(Payment).where(Payment.transaction_id == transaction_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_account_for_update(
        self, account_id: int, user_id: int
    ) -> Optional[Account]:
        query = (
            select(Account)
            .where(Account.id == account_id, Account.user_id == user_id)
            .with_for_update()
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_account(self, account: Account) -> None:
        self.session.add(account)

    async def create_payment(self, payment: Payment) -> None:
        self.session.add(payment)
