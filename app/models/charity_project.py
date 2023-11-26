from sqlalchemy import String, Column, Text

from app.core.constants import CHARITY_PROJECT_NAME_MAX_LENGTH
from app.core.db import Base
from app.models.base import CharityProjectDonationBase


class CharityProject(CharityProjectDonationBase, Base):
    name = Column(
        String(CHARITY_PROJECT_NAME_MAX_LENGTH), unique=True, nullable=False
    )
    description = Column(Text)
