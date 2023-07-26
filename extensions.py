from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
# from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler import APScheduler
jwt = JWTManager()
db = SQLAlchemy()
bcrypt = Bcrypt()
ma = Marshmallow()
scheduler = APScheduler()