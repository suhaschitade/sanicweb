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

@common_bp.route('/countries', methods=["POST"])
async def addcountry(request):
    name = request.json["name"]
    two_letter_code = request.json["two_letter_code"]
    three_letter_code = request.json["three_letter_code"]
    currency = request.json["currency"]
    active = True
    async with common_bp.pool.acquire() as connection:
        results = await connection.fetch("""
                    insert into countries("Name", two_letter_code, three_letter_code, currency, active)
                    values($1, $2, $3, $4, $5) RETURNING ID""", name,two_letter_code, three_letter_code
                    , currency, active)
        return json({'id':jsonfy(results)})

        
@common_bp.route('/getstates/<cid:int>')
async def get_states_of_country(request, cid):
    country_id = int(cid)
    async with common_bp.pool.acquire() as connection:
        results = await connection.fetch(""" 
                  select * from states where country_id = ($1) """, country_id)
        return json({'states':jsonfy(results)})

@common_bp.route('/roles')
async def get_roles(request):
    async with common_bp.pool.acquire() as connection:
        results = await connection.fetch(""" select * from roles where active=true""")
        return json({'roles':jsonfy(results)})

@common_bp.route('/companies')
async def get_companies(request):
    async with common_bp.pool.acquire as connection:
        results = await connection.fetch(""" select * from companies where active=true""")
        return json({'companies':jsonfy(results)})

@common_bp.route('/companies', methods=["OPTIONS","POST","PUT"])
async def addCompany(request):
    name = request.form.get('name')
    url = request.form.get('url')
    logo = request.files.get('logo')
  #  print (name , url)
   # print(request.files)
    active = True
    file_parameters = {
        'body':logo.body,
        'name':logo.name,
        'type':logo.type
    }
    file_name = request.files.keys()
    f = open('./uploads/'+logo.name,"wb")
    f.write(logo.body)
    f.close()


    return json({'file_name':file_name })

