from sanic import Blueprint

from buttons import btn

stock = Blueprint.group(btn, url_prefix='/stock')
