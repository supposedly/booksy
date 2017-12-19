#encoding: utf-8
permissions = [
  'manage location',
  'manage accounts',
  'manage roles',
  'create administrative roles',
  'manage media',
  'generate reports',
  ]
maximums = [
  'max renewals',
  'max checkouts',
  'max checkout duration',
  ]
acct_locks = [
  'max fines',
  'max checkouts',
  ]

async def authenticate(request, *args, **kwargs):
    """
    Authenticate a user's credentials through sanic-jwt to give them
    access to the application.
    """
    try:
        # standard fare. get username and password from the app's request
        uid = request.json['username'].lower()
        password = request.json['password'].encode('utf-8')
    except KeyError:
        # this will always be handled client-side regardless, but...
        # ...just in case, I guess
        raise jwt.exceptions.AuthenticationFailed("Missing username or password.")
    # look up the username/pw pair in the database
    async with app.pg_pool.acquire() as conn:
        query = """SELECT pwhash FROM members WHERE uid = ($1)::int"""
        try:
            if not uid.isdigit(): # convert username to ID if not already
                uid = await conn.fetch("""SELECT uid FROM members WHERE username = ($1)""")
            pwhash = await conn.fetch(query, uid)
        except: # if username/uid is invalid -- but except what in particular?
            raise exceptions.AuthenticationFailed("Invalid username or password.")
        else:
            # if valid username/pw
            query = """SELECT lid, rid, manages, email, phone FROM members WHERE uid = ($1);"""
            lid, rid, manages, email, phone = await conn.fetch(query, username)
    if bcrypt.checkpw(password, pwhash):
        # uid and rid are, as defined in `d+ds.md`, "User ID" and "Role ID"
        return {"uid": uid, "lid": lid, "rid": rid, "email": email, "phone": phone}
    # else if the password is invalid
    raise jwt.exceptions.AuthenticationFailed("Invalid username or password.")
    # (we shouldn't specify which of pw/username is invalid lest an attacker
    # use the info to enumerate possible passwords/usernames)
