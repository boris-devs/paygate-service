from fastapi import HTTPException, status

from repositories.users import UserRepository
from schemas.auth import UserLoginRequestSchema, UserLoginTokenResponseSchema
from schemas.users import UserProfileSchema
from security.passwords import verify_password
from security.token_manager import create_access_token


class UsersService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def login_user(
        self, user_data: UserLoginRequestSchema
    ) -> UserLoginTokenResponseSchema:
        """
        Authenticates the user using the provided email and password and generates
        access and refresh tokens upon successful login. This method validates
        the user's credentials, checks if the email exists, and ensures the
        provided password matches the stored password hash. Upon successful
        validation, it returns a dictionary containing the access token,
        refresh token, and token type.

        :param user_data: An instance of "UserLoginRequestSchema" containing the
            user's login credentials, including email and password.

        :return: A dictionary containing the generated access token, refresh
            token, and token type.
        :rtype: dict

        :raises HTTPException: If the user does not exist or the provided email
            and password do not match, raises an HTTP 401 error indicating
            unauthorized access.

        """
        user = await self.user_repo.get_by_email(user_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if not verify_password(user_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        access_token = create_access_token(data={"sub": str(user.id)})
        response = {"access_token": access_token, "token_type": "bearer"}
        return UserLoginTokenResponseSchema.model_validate(response)

    async def get_user_info(self, user_id: int) -> UserProfileSchema:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        return UserProfileSchema.model_validate(user)
