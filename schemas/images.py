from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.images import Images
import base64


class ImageSchema(SQLAlchemyAutoSchema):
    data = fields.Method("get_base64_data")

    def get_base64_data(self, image):
        return base64.b64encode(image.data).decode("utf-8")

    class Meta:
        model = Images
        fields = ("id", "data", "result", "created_at")


image_schema = ImageSchema()
images_schema = ImageSchema(many=True)
