from pydantic import BaseModel


class UserLoginRequestSchema(BaseModel):
    email: str
    password: str


class UserLoginTokenResponseSchema(BaseModel):
    access_token: str
    token_type: str
