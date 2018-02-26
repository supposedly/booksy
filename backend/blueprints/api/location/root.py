"""/api/location"""
import random

import sanic
import sanic_jwt as jwt
from sanic_jwt import decorators as jwtdec
from aiosmtplib.errors import SMTPRecipientsRefused
from asyncpg.exceptions import UniqueViolationError

from . import Location, Role, MediaType, MediaItem, User
from . import uid_get, rqst_get
from . import email_verify as verif

root = sanic.Blueprint('location_api', url_prefix='')

@root.get('/')
@uid_get('location')
async def give_location_repr(rqst, location):
    '''
    this.color = resp.loc.color;
        this.locname = resp.loc.name;
        this.fine_amt = String(resp.loc.fine_amt);
        this.fine_interval = String(resp.loc.fine_interval);
    '''
    return sanic.response.json({'loc': location.to_dict()}, status=200)
    
@root.post('/signup')
@rqst_get('locname', 'color', 'checkoutpw', 'adminname', 'adminpw', 'email')
async def register_location(rqst, *, locname, color, checkoutpw, adminname, adminpw, email):
    color = int(color.lstrip('#'), 16)
    try:
        token = await Location.prelim_signup(rqst, email, locname, color, checkoutpw, adminname, adminpw)
    except UniqueViolationError:
        sanic.exceptions.abort(409, "There's already a library being signed up with this email!")
    try:
        await verif.send_email(email, adminname, locname, token, loop=rqst.app.loop)
    except SMTPRecipientsRefused:
        sanic.exceptions.abort(422, "That isn't a valid email.")
    return sanic.response.raw(b'', status=204)

@root.post('/edit')
@uid_get('location', 'perms')
@rqst_get('locname', 'color', 'checkoutpw', 'fine_amt', 'fine_interval')
async def edit_location(rqst, location, perms, *, locname, color, checkoutpw, fine_amt, fine_interval):
    color = int(color.lstrip('#'), 16)
    if not perms.can_manage_location:
        sanic.exceptions.abort(403, "You aren't allowed to edit library info.")
    await location.edit(locname, color, checkoutpw, fine_amt, fine_interval)
    return sanic.response.raw(b'', status=204)

@root.get('/<attr:(name|image|color)>')
@uid_get('location')
async def return_location_attr(rqst, user, *, attr):
    return sanic.response.json({attr: getattr(location, attr)}, status=200)

@root.get('/is-registered')
async def is_location_registered(rqst):
    # .ip doesn't go past proxies, unlike rqst.remote_addr -- this is
    # good bc it allows orgs that route all traffic through a central IP
    if not rqst.ip:
        return sanic.response.json({'registered': False, 'reason': 'No IP address supplied with request'})
    location = await Location.from_ip(rqst)
    if location is not None:
        return sanic.response.json({'registered': True, 'lid': location.id}, status=200)
    else:
        return sanic.response.json({'registered': False, 'reason': 'Not found in DB'})

@root.put('/reports')
@rqst_get('get')
@uid_get('location', 'perms')
@jwtdec.protected()
async def serve_a_report(rqst, location, perms, *, get: 'type of report to get'):
    if not perms.can_generate_reports:
        sanic.exceptions.abort(403, "You aren't allowed to generate reports.")
    return sanic.response.json(await location.report(**get))

@root.get('/backups/<to_back_up:members|location|roles|holds|items>')
@uid_get('location', 'perms', user=True)
@jwtdec.protected()
async def back_up_info(rqst):
    return NotImplemented
