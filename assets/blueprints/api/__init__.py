from sanic import Blueprint

from location import loc as location
from media import md as media
from members import mbr as members
from signup import signup

api = Blueprint.group(loc, mbr, signup, url_prefix='/api')
