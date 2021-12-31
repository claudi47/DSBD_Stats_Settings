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
