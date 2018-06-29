import asyncio
import asyncpg
import datetime
import uvloop
from sanic import Sanic
from sanic.response import json
from asyncpg import connect, create_pool
from sanic import Blueprint
import os


def jsonfy(records):
    """
        This function will be used to convert records to json
    """
    return [dict(r.items()) for r in records]

user_attr_bp = Blueprint('user_attr')
app = Sanic()
app.config.from_pyfile('./config/app_config.py')
#print(app.config.DB_CONFIG)
DB_SET = app.config.DB_CONFIG

@user_attr_bp.listener("before_server_start")
async def register_db(app, loop):
    user_attr_bp.pool = await create_pool(**DB_SET, loop=loop, max_size=100)

@user_attr_bp.route('/user_attr')
async def get_user_attr(request):
    async with user_attr_bp.pool.acquire() as connection:
        results = await connection.fetch(""" select * from user_attributes where active=true """)
        return json({'userkeys':jsonfy(results)})
    
@user_attr_bp.route('/user_attr', methods=["POST"])
async def add_user_attr(request):
    role_id = request.json["role_id"]
    address_id = request.json["address_id"]
    user_id = request.json["user_id"]
    company_id = request.json["company_id"]
    active = True
    async with user_attr_bp.pool.acquire() as connection:
        results = await connection.fetch("""
                    insert into user_attributes(role_id, address_id, user_id, company_id, active)
                    values($1, $2, $3, $4, $5) RETURNING ID""", role_id,address_id, user_id
                    , company_id, active)
        return json({'id':jsonfy(results)})
    

