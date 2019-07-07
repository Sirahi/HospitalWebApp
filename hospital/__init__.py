from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_bootstrap import Bootstrap

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
api = Api(app)
bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'

from hospital import models, restfulapi, routes
