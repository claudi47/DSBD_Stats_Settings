from typing import List

import motor.motor_asyncio
from bson import ObjectId
from fastapi import FastAPI, Query
from models import BetData
import csv
import uuid

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://claudi47:ciaoatutti@cluster0.hj3kc.mongodb.net/db_dsbd?retryWrites=true&w=majority')
db = client.db_dsbd

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


@app.post("/parsing")
async def parsing_to_csv(bet_data: List[BetData]):
    # using uuid.uuid4() to get random names for our csv files
    with open(f"{uuid.uuid4()}.csv", "w", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=BetData.__fields__.keys())
        csv_writer.writeheader()
        csv_writer.writerows(data.dict() for data in bet_data)

    return csv_file.name


@app.get("/stats")
async def calculating_stats(stat: int = Query(..., le=4, ge=1)):
    match stat:
        case 1:
            names = await db['web_server_user'].find(projection=['username']).to_list(length=None)
            count_names = len(names)
            return {'names': [data['username'] for data in names], 'count': count_names}

