import flask
from flask import Flask
app = Flask(__name__)

@app.route('/')
def a():
   return flask.render_template('index.html', port='8000')
