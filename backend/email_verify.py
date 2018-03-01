import os
from email.mime.text import MIMEText

import aiosmtplib

BODY = '''
Hello, {name}!

We need to verify your email address before your library, {locname}, can be registered with Booksy. Please visit the link below:
https://booksy-db.herokuapp.com/verify?token={token}
It'll expire in approximately 24 hours.

If you didn't attempt to register a library with Booksy, please disregard this message!
'''

SENDER = 'booksy.db@gmail.com'

async def send_email(recipient, fullname, locname, token, *, loop):
    """
    Constructs a verification email to send to the aspiring admin of a
    new library.
    """
    msg = MIMEText(BODY.format(name=fullname, locname=locname, token=token))
    msg['From'] = SENDER
    msg['To'] = recipient
    msg['Subject'] = 'Verify your library registration'
    
    client = aiosmtplib.SMTP(hostname='smtp.gmail.com', port=587, use_tls=False, loop=loop)
    
    try:
        await client.connect()  # Connect to gsmtp
        await client.ehlo()     # ensure gsmtp server availability
        await client.starttls() # wait until server is ready to start TLS
        await client.ehlo()     # ensure return availability
        await client.login(SENDER, os.getenv('GMAIL_PASSWORD')) # log in / authenticate
        await client.send_message(msg, SENDER, recipient)       # send the email obj
    except:
        raise
    finally:
        await client.quit()
