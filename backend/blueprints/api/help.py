"""/help"""
# This is the only one of these API files that uses straight Postgres
# instead of outsourcing it to typedef.py. Sorta interesting I guess.

import asyncpg
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from .import uid_get, rqst_get
from .import Location, Role, MediaType, MediaItem, User

help = sanic.Blueprint('api_help', url_prefix='/help')

@help.get('/titles')
async def serve_help_titles(rqst):
    """These can be cached because they won't change"""
    async with rqst.app.acquire() as conn:
        titles = await conn.fetch("""SELECT id, title FROM help WHERE true""")
    return sanic.response.json({'articles': [{'id': i['id'], 'title': i['title']} for i in titles]}, status=200)

@help.get('/content')
@rqst_get('id')
async def serve_help_article(rqst, id_):
    """These should never be cached"""
    async with rqst.app.acquire() as conn:
        title, content = await conn.fetchrow("""SELECT title, content FROM help WHERE id = $1::bigint""", int(id_))
    return sanic.response.json({'article': {'title': title, 'content': content}}, status=200)
