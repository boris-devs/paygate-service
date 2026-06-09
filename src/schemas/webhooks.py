from decimal import Decimal
from pydantic import BaseModel, Field


class WebhookPayloadSchema(BaseModel):
    transaction_id: str = Field(min_length=1)
    account_id: int
    user_id: int
    amount: Decimal = Field(gt=0)
    signature: str = Field(min_length=64, max_length=64)

    def prepare_sign_string(self, secret_key: str) -> str:
        """
        Concatenates values in alphabetical order of their keys:
        {account_id}{amount}{transaction_id}{user_id}{secret_key}
        Note: amount must be formatted carefully (e.g., without trailing zeros if needed,
        but usually str(int) or standard string representation is fine).
        """
        # Format amount to match the signature provider's string format (e.g., "100" or "100.00")
        # In the task example, 100 becomes "100"
        amount_str = str(int(self.amount)) if self.amount % 1 == 0 else str(self.amount)

        return f"{self.account_id}{amount_str}{self.transaction_id}{self.user_id}{secret_key}"
