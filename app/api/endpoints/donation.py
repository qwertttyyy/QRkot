from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationDB, DonationAdminDB, DonationCreate
from app.services.donation import DonationService

router = APIRouter()


@router.get(
    '/',
    response_model=list[DonationAdminDB],
    dependencies=[Depends(current_superuser)],
    response_model_exclude_none=True,
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
):
    all_donations = await donation_crud.get_multi(session)
    return all_donations


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_user)],
)
async def create_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    donation_service = DonationService(session)
    created_donation = await donation_service.create_donation_obj(
        donation, user
    )
    return created_donation


@router.get(
    '/my',
    response_model=list[DonationDB],
    dependencies=[Depends(current_user)],
    response_model_exclude_none=True,
)
async def get_user_donation(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    user_donations = await donation_crud.get_donations_from_current_user(
        session, user
    )
    return user_donations
