from typing import Optional

from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDCharityProject(CRUDBase):
    async def get_charity_project_id_by_name(
        self,
        room_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        db_room_id = await session.execute(
            select(CharityProject.id).where(CharityProject.name == room_name)
        )
        db_room_id = db_room_id.scalars().first()
        return db_room_id

    async def get_projects_by_completion_rate(
        self, session: AsyncSession
    ) -> list[dict]:
        diff = extract('epoch', CharityProject.close_date) - extract(
            'epoch', CharityProject.create_date
        )
        projects = await session.execute(
            select(
                CharityProject.name,
                diff.label('fundraising_time'),
                CharityProject.description,
            )
            .where(CharityProject.fully_invested == 1)
            .order_by(diff)
        )
        return projects.all()


charity_project_crud = CRUDCharityProject(CharityProject)
