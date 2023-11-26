from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt, Extra

from app.core.constants import (
    CHARITY_PROJECT_NAME_MAX_LENGTH,
    FIELD_MIN_LENGTH,
)


class CharityProjectBase(BaseModel):
    name: str = Field(
        min_length=FIELD_MIN_LENGTH, max_length=CHARITY_PROJECT_NAME_MAX_LENGTH
    )
    description: str = Field(min_length=FIELD_MIN_LENGTH)
    full_amount: PositiveInt


class CharityProjectCreate(CharityProjectBase):
    pass


class CharityProjectUpdate(CharityProjectBase):
    name: Optional[str] = Field(
        None,
        min_length=FIELD_MIN_LENGTH,
        max_length=CHARITY_PROJECT_NAME_MAX_LENGTH,
    )
    description: Optional[str] = Field(None, min_length=FIELD_MIN_LENGTH)
    full_amount: Optional[PositiveInt]

    class Config:
        extra = Extra.forbid


class CharityProjectDB(CharityProjectBase):
    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    class Config:
        orm_mode = True
