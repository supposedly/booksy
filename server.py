import asyncio
import sanic
from sanic import response

app = sanic.Sanic(__name__)

@app.route('/')
async def test(req):
    return response.text(str(req))

app.run(host='0.0.0.0', port=8000, debug=True)
