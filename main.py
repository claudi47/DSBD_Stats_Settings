import csv
import datetime
import os
import re
import uuid
from typing import List

import motor.motor_asyncio
from bson import ObjectId
from fastapi import FastAPI, Query, HTTPException

from models import BetData, BanUser, LimitResearches, Toggle, UserBanOut, UserLimitOut, ToggleOut

app = FastAPI()
client = motor.motor_asyncio.AsyncIOMotorClient(
    f'mongodb://{os.getenv("DB_USERNAME")}:{os.getenv("DB_PASSWORD")}@{os.getenv("DB_URL")}:{os.getenv("DB_PORT")}'
    f'/{os.getenv("DB_DATABASE")}')
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
    with open(f"/tmpfiles/{uuid.uuid4()}.csv", "w", newline="") as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=BetData.__fields__.keys())
        csv_writer.writeheader()
        csv_writer.writerows(data.dict() for data in bet_data)

    return os.path.basename(csv_file.name)


@app.get("/stats")
# le = 'less equal' - ge = 'greater equal' (between 1 and 4 included)
async def calculating_stats(stat: int = Query(..., le=4, ge=1)):
    match stat:
        case 1:
            users = await db['web_server_user'].find(projection={'_id': False, 'username': True}).to_list(None)
            return {'users': users, 'count': len(users)}
        case 2:
            return await db['web_server_search'].count_documents({})
        case 3:
            researches_gb = await db['web_server_search'].count_documents({'web_site': 'goldbet'})
            researches_bw = await db['web_server_search'].count_documents({'web_site': 'bwin'})
            return {'goldbet': researches_gb, 'bwin': researches_bw}
        case 4:
            researches_count = await db['web_server_search'].count_documents({})
            users_count = await db['web_server_user'].count_documents({})
            if users_count == 0:
                return 'empty'
            users = await db['web_server_user'].aggregate([
                {
                    '$lookup': {
                        'from': 'web_server_search',
                        'localField': 'user_identifier',
                        'foreignField': 'user_id',
                        'as': 'search'
                    }
                },
                {
                    '$project': {
                        '_id': False,
                        'username': True,
                        'count': {'$size': '$search'}
                    }
                }
            ]).to_list(None)

            return {'average': researches_count / users_count, 'users': users}


@app.post("/ban", response_model=UserBanOut)
async def ban_user(ban_user: BanUser):
    def parser_date(date):
        if date == 'perma':
            return datetime.datetime.max
        period = re.search(r'(\d)y(\d)m(\d)d', date)
        years = int(period.group(1))
        months = int(period.group(2))
        days = int(period.group(3))
        return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days + months * 30 + years * 365)

    if ban_user.period == 'perma':
        period = parser_date('perma')
    elif ban_user.period != 'null':
        period = parser_date(ban_user.period)
    else:
        period = None

    await db['web_server_user'].update_one({'username': ban_user.user}, {
        '$set': {
            'ban_period': period
        }
    })

    if (updated_user := await db['web_server_user'].find_one({'username': ban_user.user})) is not None:
        return updated_user
    return HTTPException(status_code=404, detail='User not found')


@app.post("/researches", response_model=UserLimitOut)
async def limit_researches(max_res: LimitResearches):
    await db['web_server_user'].update_one({'username': max_res.user}, {
        '$set': {
            'max_research': max_res.limit
        }
    })
    if (updated_user := await db['web_server_user'].find_one({'username': max_res.user})) is not None:
        return updated_user
    return HTTPException(status_code=404, detail='User not found')


@app.post("/toggle", response_model=ToggleOut)
async def toggle_website(toggle: Toggle):
    if toggle.state == 'disable':
        state = False
    elif toggle.state == 'enable':
        state = True
    if toggle.web_site == 'goldbet':
        await db['web_server_settings'].update_one({}, {
            '$set': {
                'goldbet_research': state
            }
        })
    else:
        await db['web_server_settings'].update_one({}, {
            '$set': {
                'bwin_research': state
            }
        })

    if (updated_setting := await db['web_server_settings'].find_one()) is not None:
        return updated_setting
    return HTTPException(status_code=404, detail='Setting not found')
