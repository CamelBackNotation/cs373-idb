from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache
from server.views import index
import pymysql

app = Flask(__name__, static_url_path="/static", static_folder="static")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@mysqlserver/swe'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

app.register_blueprint(index)
db = SQLAlchemy(app)

from server.bin_gamers_api import api
app.register_blueprint(api.blueprint, url_prefix='/api')
