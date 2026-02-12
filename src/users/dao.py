from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from src.users.models.user import User
from src.users.auth.schemas import SUserRegister, UserOut
from src.users.auth.auth import get_password_hash 

class UserDAO:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()

    async def get_users_list(self) -> List[UserOut] | None:
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def create_user(self, user: SUserRegister) -> User | None:
        user = User(
        email=user.email,
        password=get_password_hash(user.password),
        phone_number=user.phone_number,
        first_name=user.first_name,
        last_name=user.last_name,
    )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
