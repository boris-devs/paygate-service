from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, Numeric, text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.users import User


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    balance: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2),
        default=Decimal("0.00"),
        server_default=text("0.00"),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="accounts")
    payments: Mapped[List["Payment"]] = relationship(back_populates="account")

    def __repr__(self) -> str:
        return f"<Account id={self.id} user_id={self.user_id} balance={self.balance}>"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    transaction_id: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )

    account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id", ondelete="RESTRICT"), nullable=False, index=True
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=2), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(),
        server_default=text("TIMEZONE('utc', now())"),
        nullable=False,
    )

    account: Mapped["Account"] = relationship(back_populates="payments")

    def __repr__(self) -> str:
        return f"<Payment id={self.id} transaction_id={self.transaction_id} amount={self.amount}>"
