from typing import Optional

from aiogoogle import Aiogoogle
from fastapi import HTTPException
from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject
from app.schemas.charity_project import (
    CharityProjectCreate,
    CharityProjectUpdate,
)
from app.services.google_api import (
    spreadsheets_create,
    set_user_permissions,
    spreadsheets_update_value,
)
from app.services.investing import investing
from app.services.utilities import convert_fundraising_time_projects


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

    async def check_name_duplicate(
        self,
        charity_project: str,
        session: AsyncSession,
    ) -> None:
        charity_project_id = (
            await charity_project_crud.get_charity_project_id_by_name(
                charity_project, session
            )
        )
        if charity_project_id is not None:
            raise HTTPException(
                status_code=400,
                detail='Проект с таким именем уже существует!',
            )

    async def get_charity_project_or_404(
        self, charity_project_id: int, session: AsyncSession
    ) -> CharityProject:
        charity_project = await charity_project_crud.get(
            charity_project_id, session
        )
        if charity_project is None:
            raise HTTPException(status_code=404, detail='Проект не найден!')
        return charity_project

    async def check_project_is_already_invested(
        self,
        charity_project: CharityProject,
    ) -> None:
        if charity_project.invested_amount > 0:
            raise HTTPException(
                status_code=400,
                detail='В проект были внесены средства, не подлежит удалению!',
            )

    async def check_project_before_update(
        self, charity_project: CharityProject, obj_in: CharityProjectUpdate
    ) -> None:
        if charity_project.fully_invested:
            raise HTTPException(
                status_code=400, detail='Закрытый проект нельзя редактировать!'
            )
        if obj_in.full_amount:
            if obj_in.full_amount < charity_project.invested_amount:
                raise HTTPException(
                    status_code=400,
                    detail='Нельзя установить сумму меньше вложенной',
                )

    async def charity_project_create(
        self, charity_project: CharityProjectCreate, session: AsyncSession
    ):
        await self.check_name_duplicate(charity_project.name, session)
        new_charity_project = await self.create(charity_project, session)
        await investing(new_charity_project, session)
        return new_charity_project

    async def charity_project_remove(
        self, charity_project_id: int, session: AsyncSession
    ):
        charity_project = await self.get_charity_project_or_404(
            charity_project_id, session
        )
        await self.check_project_is_already_invested(charity_project)
        return charity_project

    async def charity_project_update(
        self,
        charity_project_id: int,
        session: AsyncSession,
        obj_in: CharityProjectUpdate,
    ):
        charity_project = await self.get_charity_project_or_404(
            charity_project_id, session
        )
        if obj_in.name:
            await self.check_name_duplicate(obj_in.name, session)

        await self.check_project_before_update(charity_project, obj_in)
        charity_project = await self.update(charity_project, obj_in, session)
        return charity_project

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

    async def get_charity_projects_and_report(
        self, session: AsyncSession, wrapper_services: Aiogoogle
    ):
        projects = await self.get_projects_by_completion_rate(session)
        projects = convert_fundraising_time_projects(projects)
        spreadsheetid = await spreadsheets_create(wrapper_services)
        await set_user_permissions(spreadsheetid, wrapper_services)
        await spreadsheets_update_value(
            spreadsheetid, projects, wrapper_services
        )
        return projects


charity_project_crud = CRUDCharityProject(CharityProject)
