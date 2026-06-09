import enum
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base

if TYPE_CHECKING:
	from src.models.billing import Account

class UserRole(str, enum.Enum):
	USER = "user"
	ADMIN = "admin"


class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
	password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
	full_name: Mapped[str] = mapped_column(String(255), nullable=False)
	role: Mapped[UserRole] = mapped_column(
		Enum(UserRole),
		default=UserRole.USER,
		server_default=UserRole.USER.value,
		nullable=False
	)

	accounts: Mapped[List["Account"]] = relationship(
		back_populates="user",
		cascade="all, delete-orphan"
	)

	def __repr__(self) -> str:
		return f"<User id={self.id} email={self.email} role={self.role}>"
