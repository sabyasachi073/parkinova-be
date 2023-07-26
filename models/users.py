from extensions import db

class User(db.Model) :
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(60),nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    