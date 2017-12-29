from sanic import Blueprint

from api import api
from stock import stock

bp = Blueprint.group(api, stock, url_prefix='/api')
