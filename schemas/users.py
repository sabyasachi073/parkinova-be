from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from models.users import User


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ("id", "full_name", "email")


user_schema = UserSchema()
users_schema = UserSchema(many=True)
