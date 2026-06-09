from pydantic import EmailStr, BaseModel


class UserProfileSchema(BaseModel):
	id: int
	email: EmailStr
	full_name: str

	class Config:
		from_attributes = True
