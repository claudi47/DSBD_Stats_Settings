import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from main import PyObjectId


class BetData(BaseModel):
    date: str
    match: str
    one: str
    ics: str
    two: str
    gol: str
    over: str
    under: str


class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    username: str
    user_identifier: str
    max_research: int
    ban_period: datetime
    timestamp: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserBanOut(BaseModel):
    username: str
    ban_period: Optional[datetime.datetime]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class BanUser(BaseModel):
    user: str
    period: str


class LimitResearches(BaseModel):
    user: str
    limit: int


class UserLimitOut(BaseModel):
    username: str
    max_research: int

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class Toggle(BaseModel):
    state: str
    web_site: str


class ToggleOut(BaseModel):
    goldbet_research: bool
    bwin_research: bool

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}