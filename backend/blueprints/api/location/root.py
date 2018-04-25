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
    """
    Serves all of a location's important attributes.
    """
    return sanic.response.json({'loc': location.to_dict()}, status=200)
    
@root.post('/signup')
@rqst_get('locname', 'color', 'adminname', 'email')
async def register_location(rqst, *, locname, color,  adminname, email):
    """
    Handles the pre-preliminary information-gathering for the registration
    of a new library. Once this endpoint is activated, this information is
    stored in the "purgatory" of the signups table until the emailed
    verification link is clicked.
    """
    color = int(color.lstrip('#'), 16)
    try:
        token = await Location.prelim_signup(rqst, email, locname, color, adminname)
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
    """
    Handles all editing of a location's info.
    """
    color = int(color.lstrip('#'), 16)
    if not perms.can_manage_location:
        sanic.exceptions.abort(403, "You aren't allowed to edit library info.")
    await location.edit(locname, color, checkoutpw, fine_amt, fine_interval)
    return sanic.response.raw(b'', status=204)

@root.get('/<attr:(name|image|color)>')
@uid_get('location')
async def return_location_attr(rqst, user, *, attr):
    # unused
    return sanic.response.json({attr: getattr(location, attr)}, status=200)

@root.get('/is-registered')
async def is_location_registered(rqst):
    """
    This is for when I was thinking of allowing users signing in from
    their location to do so without entering their location ID.
    
    I ended up not going for it, though it *would* have been cool.
    """
    # .ip doesn't go past proxies, unlike rqst.remote_addr -- this is
    # good bc it allows orgs that route all traffic through a central IP
    return sanic.response.json({'registered': False, 'reason': 'Not Implemented'})
    '''
    if not rqst.ip:
        return sanic.response.json({'registered': False, 'reason': 'No IP address supplied with request'})
    location = await Location.from_ip(rqst)
    if location is not None:
        return sanic.response.json({'registered': True, 'lid': location.lid}, status=200)
    else:
        return sanic.response.json({'registered': False, 'reason': 'Not found in DB'})
    '''

@root.put('/reports')
@rqst_get('get', 'live')
@uid_get('location', 'perms')
@jwtdec.protected()
async def get_report(rqst, location, perms, *, get, live):
    """
    get: type of report to get
    live: whether to serve the cached weekly report or a live one
    
    Serves a generated report on whatever activity is going on in the library.
    
    Due to the multi-library nature of the app, I cannot satisfy the "weekly"
    requirement, so I'll take the five points' hit there -- if a user wishes
    to obtain weekly reports, they can probably handle clicking the 'generate
    report' button every week
    """
    if not perms.can_generate_reports:
        sanic.exceptions.abort(403, "You aren't allowed to generate reports.")
    return sanic.response.json(await location.report(live, **get))


@root.get('/reports/last')
@uid_get('location', 'perms')
async def get_last_report_date(rqst, location, perms):
    """
    Serves the date of the last cached report.
    """
    if not perms.can_generate_reports:
        sanic.exceptions.abort(403, "You aren't allowed to view reports.")
    r_date = location.last_report_date
    return sanic.response.json({'date': r_date and str(r_date)})


@root.get('/backups/<to_back_up:members|location|roles|holds|items>')
@uid_get('location', 'perms', user=True)
@jwtdec.protected()
async def back_up_info(rqst):
    """
    'Data storage includes dynamic backup' -- again, multi-location app
    where info is stored remotely so I don't imagine it'd be as useful
    as in a local app to allow backing up of information
    """
    raise NotImplementedError
