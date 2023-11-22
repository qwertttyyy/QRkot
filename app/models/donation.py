from sqlalchemy import Column, Integer, ForeignKey, Text

from app.core.db import Base
from app.models.base import CharityProjectDonationBase


class Donation(CharityProjectDonationBase, Base):
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)
