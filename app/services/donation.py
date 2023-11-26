from typing import Optional

from app.crud.base import CRUDBase
from app.crud.donation import donation_crud
from app.models import User, CharityProject
from app.services.investing import investing


class DonationService:
    def __init__(self, session):
        self.session = session

    async def create_donation_obj(self, donation, user: Optional[User] = None):
        new_donation = await donation_crud.create(donation, self.session, user)

        unclosed_charity_projects = await CRUDBase(
            CharityProject
        ).get_unclosed_objects(self.session)
        donation = investing(new_donation, unclosed_charity_projects)
        await self.session.commit()
        await self.session.refresh(donation)
        return new_donation
