import asyncio
import asyncpg
import datetime
import uvloop
from sanic import Sanic
from sanic.response import json
from asyncpg import connect, create_pool
from sanic import Blueprint

def jsonfy(records):
    """
        This function will be used to convert records to json
    """
    return [dict(r.items()) for r in records]


common_bp = Blueprint('common')

app = Sanic()

app.config.from_pyfile('./config/app_config.py')
#print(app.config.DB_CONFIG)
DB_SET = app.config.DB_CONFIG
#print(DB_SET)


@common_bp.listener('before_server_start')
async def register_db(app, loop):
    common_bp.pool = await create_pool(**DB_SET, loop=loop, max_size=100)

@common_bp.route('/countries')
async def get(request):
    async with common_bp.pool.acquire() as connection:
        results = await connection.fetch('select * from countries')
        return json({'countries':jsonfy(results)})


    

