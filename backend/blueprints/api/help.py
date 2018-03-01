# Note, this is the only one of these route-handler files that uses
# straight Postgres instead of outsourcing it to the classes in typedef.
import asyncpg
import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec

from . import uid_get, rqst_get
from . import Location, Role, MediaType, MediaItem, User

help = sanic.Blueprint('api_help', url_prefix='/help')

@help.get('/titles')
async def serve_help_titles(rqst):
    """
    These can be cached because they won't change
    """
    titles = await rqst.app.pg_pool.fetch('''SELECT id, title FROM help WHERE true''')
    return sanic.response.json({'articles': [{'id': i['id'], 'title': i['title']} for i in titles]}, status=200)

@help.get('/content')
@rqst_get('ID')
async def serve_help_article(rqst, *, ID):
    """
    These should never be cached.
    """
    title, content = await rqst.app.pg_pool.fetchrow('''SELECT title, content FROM help WHERE id = $1::bigint''', int(ID))
    return sanic.response.json({'help': {'title': title, 'content': content}}, status=200)

@help.get('/brief')
@rqst_get('ID')
async def give_brief(rqst, *, ID):
    """
    For the "What's this?" tooltips; serves a brief explanation
    of whatever's on the page and links to its full help article.
    """
    resp = await rqst.app.pg_pool.fetchrow('''SELECT title, brief FROM help WHERE id = $1::bigint''', int(ID))
    return sanic.response.json({'help': {'title': resp['title'], 'brief': resp['brief']}})
