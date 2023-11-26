from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.services.charity_project import CharityProjectService

router = APIRouter()


@router.get(
    '/',
    response_model=list[dict],
    dependencies=[Depends(current_superuser)],
)
async def get_report(
    session: AsyncSession = Depends(get_async_session),
    wrapper_services: Aiogoogle = Depends(get_service),
):
    charity_project_service = CharityProjectService(session)
    projects = await charity_project_service.get_charity_projects_and_report(
        wrapper_services
    )
    return projects
