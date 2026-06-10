import asyncio
from sqlalchemy import select

from src.security.passwords import hash_password
from src.db.session_postgres import AsyncSessionLocal
from src.models.users import User, UserRole
from src.models.billing import Account


async def seed_data():
	print("Run seed data...")

	dummy_hash = hash_password("password123")

	async with AsyncSessionLocal() as session:
		async with session.begin():
			result = await session.execute(select(User).where(User.email == "user@test.com"))
			existing_user = result.scalar_one_or_none()

			if existing_user:
				print("Test data already exists!")
				return

			test_user = User(
				email="user@test.com",
				password_hash=dummy_hash,
				full_name="Test User",
				role=UserRole.USER
			)

			test_admin = User(
				email="admin@test.com",
				password_hash=dummy_hash,
				full_name="Test Admin",
				role=UserRole.ADMIN
			)

			session.add_all([test_user, test_admin])
			await session.flush()

			test_account = Account(
				user_id=test_user.id,
				balance=0.00
			)
			session.add(test_account)

			print("Test data successfully added!")


if __name__ == "__main__":
	asyncio.run(seed_data())