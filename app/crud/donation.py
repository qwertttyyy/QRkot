from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import Donation, User
from app.services.investing import investing


class CRUDDonation(CRUDBase):
    async def get_donations_from_current_user(
        self, session: AsyncSession, user: User
    ):
        donations = await session.execute(
            select(self.model).where(self.model.user_id == user.id)
        )
        return donations.scalars().all()

    async def create_donation_obj(
        self, donation, session: AsyncSession, user: Optional[User] = None
    ):
        new_donation = await self.create(donation, session, user)
        await investing(new_donation, session)
        return new_donation


donation_crud = CRUDDonation(Donation)
