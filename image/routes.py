import os
import shutil
from datetime import datetime, timezone

from flask import jsonify, Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from tensorflow.keras.models import load_model
import numpy as np
import cv2

from models.users import User
from models.images import Images
from schemas.images import images_schema
from extensions import db
import mimetypes
import pytz

image = Blueprint("image", __name__)


@image.route("/test", methods=["GET"])
@jwt_required()
def test():
    current_user = get_jwt_identity()
    response = jsonify(message="success", logged_in_as=current_user)
    return response, 200


@image.route("/upload", methods=["POST"])
@jwt_required()
def upload():
    files = request.files.getlist("image")
    image_ids = []
    images = []

    # folder to upload images temporarily to
    folder = 'uploads'

    # check if uploads folder already exists
    if os.path.exists(os.path.join('.', folder)):
        shutil.rmtree(os.path.join('.', folder))
    
    os.mkdir(os.path.join('.', folder))


    if files:
        email = get_jwt_identity()
        user_id = User.query.filter_by(email=email).first().id
        now = datetime.now(timezone.utc)
        ist = pytz.timezone("Asia/Kolkata")
        created_at = now.astimezone(ist)
        for file in files:
            # save the file
            file.save(os.path.join(folder, file.filename))

            mimetype = mimetypes.guess_type(file.filename)[0]
            image = Images(
                user_id=user_id,
                data=file.read(),
                result=0.0,
                mime_type=mimetype,
                created_at=created_at,
            )

            db.session.add(image)
            db.session.commit()
            
            image_ids.append(image.id)
        
        for image in os.listdir(os.path.join('.', folder)):
            img = cv2.imread(os.path.join('.', folder, image), cv2.IMREAD_GRAYSCALE)
            resize = cv2.resize(img, (256, 256))
            images.append(resize)

        np_images = np.array(images)

        parkinova_model = load_model(os.path.join('.', 'ml', 'park_steady.h5'))
        yhat = parkinova_model.predict(np_images)


        for i in range(len(image_ids)):
            image = Images.query.get(image_ids[i])
            image.result = yhat[i][0].astype(float)

            db.session.commit()

        return jsonify(message="Images uploaded successfully"), 200

    return jsonify(message="Failed to upload image"), 400


@image.route("/fetch-others", methods=["GET"])
@jwt_required()
def fetch_images():
    email = get_jwt_identity()
    user_id = User.query.filter_by(email=email).first().id

    images = (
        Images.query.filter_by(user_id=user_id)
        .order_by(Images.id.desc())
        .offset(3)
        .all()
    )

    if images:
        response = images_schema.dump(images)
        return jsonify(response), 200

    return jsonify(message="No images found"), 404


@image.route("/fetch-latest", methods=["GET"])
@jwt_required()
def fetch_lst_image():
    email = get_jwt_identity()
    user_id = User.query.filter_by(email=email).first().id

    images = (
        Images.query.filter_by(user_id=user_id)
        .order_by(Images.id.desc())
        .limit(3)
        .all()
    )
    if image:
        response = images_schema.dump(images)
        return jsonify(response), 200

    return jsonify(message="No images found"), 404
