from aiogoogle import Aiogoogle
from fastapi import HTTPException

from app.core.constants import DEFAULT_INVESTED_AMOUNT
from app.crud.base import CRUDBase
from app.crud.charity_project import charity_project_crud
from app.models import CharityProject, Donation
from app.schemas.charity_project import (
    CharityProjectUpdate,
    CharityProjectCreate,
)
from app.services.google_api import (
    spreadsheets_create,
    set_user_permissions,
    spreadsheets_update_value,
)
from app.services.investing import investing
from app.services.utilities import convert_fundraising_time_projects


class CharityProjectService:
    def __init__(self, session):
        self.session = session

    async def _check_name_duplicate(
        self,
        charity_project: str,
    ) -> None:
        charity_project_id = (
            await charity_project_crud.get_charity_project_id_by_name(
                charity_project, self.session
            )
        )
        if charity_project_id is not None:
            raise HTTPException(
                status_code=400,
                detail='Проект с таким именем уже существует!',
            )

    async def _get_charity_project_or_404(
        self, charity_project_id: int
    ) -> CharityProject:
        charity_project = await charity_project_crud.get(
            charity_project_id, self.session
        )
        if charity_project is None:
            raise HTTPException(status_code=404, detail='Проект не найден!')
        return charity_project

    async def _check_project_is_already_invested(
        self,
        charity_project: CharityProject,
    ) -> None:
        if charity_project.invested_amount > DEFAULT_INVESTED_AMOUNT:
            raise HTTPException(
                status_code=400,
                detail='В проект были внесены средства, не подлежит удалению!',
            )

    async def _check_project_before_update(
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
        self, charity_project: CharityProjectCreate
    ):
        await self._check_name_duplicate(charity_project.name)
        new_charity_project = await charity_project_crud.create(
            charity_project, self.session
        )
        unclosed_donations = await CRUDBase(Donation).get_unclosed_objects(
            self.session
        )
        charity_project = investing(new_charity_project, unclosed_donations)
        await self.session.commit()
        await self.session.refresh(charity_project)
        return new_charity_project

    async def charity_project_remove(self, charity_project_id: int):
        charity_project = await self._get_charity_project_or_404(
            charity_project_id
        )
        await self._check_project_is_already_invested(charity_project)
        return charity_project

    async def charity_project_update(
        self,
        charity_project_id: int,
        obj_in: CharityProjectUpdate,
    ):
        charity_project = await self._get_charity_project_or_404(
            charity_project_id
        )
        if obj_in.name:
            await self._check_name_duplicate(obj_in.name)

        await self._check_project_before_update(charity_project, obj_in)
        charity_project = await charity_project_crud.update(
            charity_project, obj_in, self.session
        )
        return charity_project

    async def get_charity_projects_and_report(
        self, wrapper_services: Aiogoogle
    ):
        projects = await charity_project_crud.get_projects_by_completion_rate(
            self.session
        )
        projects = convert_fundraising_time_projects(projects)
        spreadsheetid = await spreadsheets_create(wrapper_services)
        await set_user_permissions(spreadsheetid, wrapper_services)
        await spreadsheets_update_value(
            spreadsheetid, projects, wrapper_services
        )
        return projects
