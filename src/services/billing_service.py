import hashlib

from fastapi import HTTPException
from fastapi import status
from core.settings import settings
from models.billing import Payment, Account
from repositories.users import UserRepository
from schemas.webhooks import WebhookPayloadSchema
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

    def _verify_signature(self, payload: WebhookPayloadSchema) -> bool:
        """
         Verify the HMAC-like signature of a webhook payload.

         The method:
         - Asks the payload to produce the canonical sign string via
          `payload.prepare_sign_string(settings.SECRET_KEY)`.
         - Computes SHA-256 hex digest of that string.
         - Compares it to the `payload.signature` provided.

         Parameters:
         - payload: The webhook payload object (expected to implement
          `prepare_sign_string` and include a `signature` attribute).

         Returns:
        - True if the computed hash matches the payload signature, False otherwise.
        """
        sign_string = payload.prepare_sign_string(settings.SECRET_KEY)
        generated_hash = hashlib.sha256(sign_string.encode("utf-8")).hexdigest()
        return generated_hash == payload.signature

    async def process_webhook(self, payload: WebhookPayloadSchema, user_repo: UserRepository) -> dict:
        """
        Process an incoming payment webhook.

        Workflow:
        1. Verify the payload signature to ensure authenticity.
        2. Check idempotency by ensuring the transaction_id hasn't already been processed.
        3. Ensure the referenced user exists.
        4. Acquire (and lock for update) the target account for the user.
           - If the account does not exist, create it with the initial balance equal
             to the payment amount.
           - If the account exists, increment its balance by the payment amount.
        5. Create a Payment record tied to the account and transaction_id.
        6. Commit the repository session to persist changes.
        7. Return a success dict containing status and a human-readable detail.

        Parameters:
        - payload: `WebhookPayloadSchema` instance containing:
            - transaction_id: unique transaction identifier.
            - account_id: target account ID.
            - user_id: ID of the user owning the account.
            - amount: numeric amount to credit.
            - signature: HMAC/signature to validate authenticity.

        Returns:
        - dict: {"status": "success", "detail": <message>} on success.

        Raises:
        - HTTPException(status.HTTP_400_BAD_REQUEST) if signature is invalid or
          transaction already processed.
        - HTTPException(status.HTTP_404_NOT_FOUND) if the referenced user does not exist.

        Concurrency and idempotency notes:
        - This method relies on repository methods such as `get_account_for_update`
          to provide necessary row-level locking or other concurrency control to avoid
          race conditions when updating balances.
        - The idempotency check (lookup by transaction_id) prevents double-processing
          of the same webhook.
        """
        if not self._verify_signature(payload):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid signature"
            )

        existing_payment = await self.billing_repo.get_payment_by_transaction_id(
            payload.transaction_id
        )
        if existing_payment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction already processed",
            )

        user = await user_repo.get_by_id(payload.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        account = await self.billing_repo.get_account_for_update(
            account_id=payload.account_id, user_id=payload.user_id
        )

        if not account:
            account = Account(
                id=payload.account_id, user_id=payload.user_id, balance=payload.amount
            )
            await self.billing_repo.create_account(account)
        else:
            account.balance += payload.amount

        new_payment = Payment(
            transaction_id=payload.transaction_id,
            account_id=account.id,
            amount=payload.amount,
        )
        await self.billing_repo.create_payment(new_payment)

        await self.billing_repo.session.commit()

        return {
            "status": "success",
            "detail": f"Account {account.id} successfully credited",
        }
