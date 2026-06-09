from typing import List
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
