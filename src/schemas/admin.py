from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from src.models.users import UserRole


class AdminAccountResponseSchema(BaseModel):
	id: int
	balance: Decimal

	class Config:
		from_attributes = True


class AdminUserResponseSchema(BaseModel):
	id: int
	email: EmailStr
	full_name: str
	role: UserRole
	accounts: List[AdminAccountResponseSchema] = []

	class Config:
		from_attributes = True


class UserCreateSchema(BaseModel):
	email: EmailStr
	password: str = Field(min_length=6)
	full_name: str = Field(min_length=2)
	role: UserRole = UserRole.USER


class UserUpdateSchema(BaseModel):
	email: Optional[EmailStr] = None
	password: Optional[str] = Field(None, min_length=6)
	full_name: Optional[str] = Field(None, min_length=2)
	role: Optional[UserRole] = None
