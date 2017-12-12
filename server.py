import sanic, asyncio, uvloop
import os
from sanic import response

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
app = sanic.Sanic(__name__)

app.static('/favicon.ico', './favicon.ico')
app.static('/icons', './icons')

@app.route('/')
async def test(request):
    return response.html('''
    <html>
        <head>
            <link rel="apple-touch-icon" sizes="120x120" href="/icons/apple-touch-icon.png">
            <link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32x32.png">
            <link rel="icon" type="image/png" sizes="16x16" href="/icons/favicon-16x16.png">
            <link rel="manifest" href="/icons/manifest.json">
            <link rel="mask-icon" href="/icons/safari-pinned-tab.svg" color="#5bbad5">
            <link rel="shortcut icon" href="/icons/favicon.ico">
            <meta name="apple-mobile-web-app-title" content="Booksy">
            <meta name="application-name" content="Booksy">
            <meta name="msapplication-config" content="/icons/browserconfig.xml">
            <meta name="theme-color" content="#ffffff">
        </head>
        <body>
            <h1>Hello world!</h1>
        </body>
    </html>
    ''')

app.run(host='0.0.0.0', port=os.environ.get('PORT', 8000), debug=True)
