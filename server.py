import asyncio
import sanic
import os
from sanic import response

app = sanic.Sanic(__name__)

@app.route('/')
async def test(req):
    return response.text('Hello world!')

print(os.environ)
app.run(host='0.0.0.0', port=os.environ.get('PORT', 8000), debug=True)
