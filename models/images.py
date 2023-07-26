from extensions import db


class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    data = db.Column(db.LargeBinary(length=10485760))
    result = db.Column(db.Float)
    mime_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, nullable=False)
