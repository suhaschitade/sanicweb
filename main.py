import asyncio
import asyncpg
import datetime
import uvloop
from sanic import Sanic
from sanic.response import json
from asyncpg import connect, create_pool
from common import common_bp
from user_attr import user_attr_bp



def jsonfy(records):
    """
        This function will be used to convert records to json
    """
    return [dict(r.items()) for r in records]

app = Sanic(__name__)

app.config.from_pyfile('./config/app_config.py')
print(app.config.DB_CONFIG)
DB_SET = app.config.DB_CONFIG
print(DB_SET)



@app.listener('before_server_start')
async def register_db(app, loop):
    app.pool = await create_pool(**DB_SET, loop=loop, max_size=100)



@app.route("/")
async def userGet(request):
    async with app.pool.acquire() as connection:
        results = await connection.fetch('select * from users')
        return json({'users':jsonfy(results)})

@app.route("/", methods=["POST"])
async def createuser(request):
   # print(request.body)
    first_name = request.json['first_name']
    last_name = request.json["last_name"]
    print(request.json)
    print(first_name)

    async with app.pool.acquire() as connection:
        results = await connection.fetch("""
                    Insert into users(first_name, last_name) values
                    ($1, $2) 
                    RETURNING id""", first_name, last_name)

    return json({"user": jsonfy(results)})


app.blueprint(common_bp)
app.blueprint(user_attr_bp)



if __name__ == "__main__":
    app.run(host="localhost",port=8000)

