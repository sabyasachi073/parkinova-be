from flask import request, jsonify, Blueprint
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt,
    get_jwt_identity,
)
from datetime import datetime
from datetime import timezone
import pytz

from extensions import db, bcrypt, jwt
from models.users import User
from models.tokenblocklist import TokenBlocklist
from schemas.users import user_schema


auth = Blueprint("auth", __name__)


@auth.route("/signup", methods=["POST"])
def signup():
    full_name = request.json["fullName"]
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()
    if user:
        message = "user already exists"
        code = 403

    else:
        hashed_password = bcrypt.generate_password_hash(password)
        newuser = User(full_name=full_name, email=email, password=hashed_password)
        db.session.add(newuser)
        db.session.commit()

        message = "signup successful"
        code = 200

    return jsonify({"message": message}), code


@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None


@auth.route("/signin", methods=["POST"])
def signin():
    email = request.json["email"]
    password = request.json["password"]

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(user.password, password):
        access_token = create_access_token(identity=email)
        response = jsonify(message="login successful", access_token=access_token)
        code = 200
    elif user:
        response = jsonify(message="incorrect password")
        code = 401
    else:
        response = jsonify(message="user doesn't exists")
        code = 404

    return response, code


@auth.route("/logout", methods=["DELETE"])
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    expiry_time = get_jwt()["exp"]
    expiry_datetime = datetime.fromtimestamp(expiry_time, timezone.utc)
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now, expires_at=expiry_datetime))
    db.session.commit()
    return jsonify(msg="JWT revoked")


@auth.route("/fetch-user", methods=["GET"])
@jwt_required()
def fetch_user():
    current_user = get_jwt_identity()
    user_details = User.query.filter_by(email=current_user).first()  # Fetch the user

    if user_details:
        response = user_schema.dump(user_details)
        return jsonify(response), 200

    return jsonify(message="User not found"), 404
