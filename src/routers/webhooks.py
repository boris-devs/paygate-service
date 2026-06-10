from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.db import get_db
from src.repositories.billing import BillingRepository
from src.repositories.users import UserRepository
from src.services.billing_service import BillingService
from src.schemas.webhooks import WebhookPayloadSchema, WebhookResponseSchema

router = APIRouter()


def get_billing_service(session: AsyncSession = Depends(get_db)) -> BillingService:
	billing_repo = BillingRepository(session)
	return BillingService(
		billing_repo=billing_repo,
	)

def get_user_repo(session: AsyncSession = Depends(get_db)) -> UserRepository:
	return UserRepository(session)


@router.post(
	"/payment/",
	status_code=status.HTTP_200_OK,
	summary="Handle incoming third-party payment webhook",
	response_model=WebhookResponseSchema
)
async def payment_webhook(
		payload: WebhookPayloadSchema,
		billing_service: BillingService = Depends(get_billing_service),
		user_repo: UserRepository = Depends(get_user_repo),
) ->  WebhookResponseSchema:
	"""
	Endpoint for third-party payment system to notify about successful user deposits.
	Validates signature, ensures idempotency, and credits user balance safely.
	"""
	return await billing_service.process_webhook(payload, user_repo=user_repo)
