import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel


class BetData(BaseModel):
    date: str
    match: str
    one: str
    ics: str
    two: str
    gol: str
    over: str
    under: str

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