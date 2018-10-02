import asyncio
import asyncpg
import datetime
import uvloop
import datetime
from sanic import Sanic
from sanic.response import json
from asyncpg import connect, create_pool
from sanic import Blueprint
from sanic_cors import CORS, cross_origin

def jsonify(records):
    return [dict(r.items()) for r in records ]

article_bp = Blueprint('article')

app = Sanic()
CORS(app)

app.config.from_pyfile('./config/app_config.py')

DB_SET = app.config.DB_CONFIG

@article_bp.listener('before_server_start')
async def register_db(app, loop):
    article_bp.pool = await create_pool(**DB_SET, loop=loop,max_size=100)

@article_bp.route('/articles', methods=["GET", "OPTIONS"])
async def get_articles(request):
    async with article_bp.pool.acquire() as connection:
        results = await connection.fetch('select * from articles where active=true')
        return json({'articles':jsonify(results)})

@article_bp.route('/post_articles', methods=["OPTIONS","POST","PUT"])
async def post_article(request):
    title = request.form.get('title')
    short_descr = request.form.get('short_descr')
    descr = request.form.get('descr')
    active = True
    is_live = request.form.get('is_live')
    articleImage = request.files.get('image')
    created_at = datetime.datetime.strftime("%Y-%M-%D")


    file_parameters = {
        'body':articleImage.body,
        'name':articleImage.name,
        'type':articleImage.type
    }
    file_name = request.file.keys()
    f = open('./uploads/articles/'+articleImage.name+'wb')
    f.write(articleImage.body)
    f.close()
    async with article_bp.pool.acquire() as connection:
        results = await connection.fetch(""" insert into articles(title, short_descr, descr, owner, created_at, updated_at, active, image, is_live)
        values ($1,$2,$3,$4,$5,$6,$7,$8,$9) returning id """, title, short_descr, descr, 1, created_at, created_at, active, articleImage.name, is_live)
        return json({'id':results})








    

