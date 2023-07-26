from flask import Flask, jsonify
from extensions import jwt, db, bcrypt, ma, scheduler
from datetime import timedelta
import os
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException
from flask_cors import CORS

from image.routes import image
from auth.routes import auth

from functions.deleteoldtokens import delete_old_tokens


def create_app():
    load_dotenv()
    app = Flask(__name__)
    CORS(app)

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
    app.config["SCHEDULER_images_ENABLED"] = True
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    ma.init_app(app)
    scheduler.init_app(app)

    scheduler.add_job(
        func=delete_old_tokens,
        id="id_delete_old_tokens",
        trigger="interval",
        hours=12,
    )

    # Starting Scheduler
    scheduler.start()

    @app.errorhandler(Exception)
    def handle_error(e):
        code = 500
        if isinstance(e, HTTPException):
            code = e.code
        return jsonify(error=str(e)), code

    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(image, url_prefix="/image")

    return app
