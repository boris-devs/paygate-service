from src.repositories.billing import BillingRepository
from src.schemas.billings import AccountsResponseSchema, PaymentsResponseSchema


class BillingService:
	def __init__(self, billing_repo: BillingRepository):
		self.billing_repo = billing_repo

	async def get_user_accounts(self, user_id: int) -> list[AccountsResponseSchema]:
		accounts = await self.billing_repo.get_user_accounts(user_id)
		return [AccountsResponseSchema.model_validate(acc) for acc in accounts]

	async def get_user_payments(self, user_id: int) -> list[PaymentsResponseSchema]:
		payments = await self.billing_repo.get_user_payments(user_id)

		return [PaymentsResponseSchema.model_validate(p) for p in payments]
