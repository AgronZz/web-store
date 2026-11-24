from extensions import db

class Gender(db.Model):
    __tablename__ = "genders"

    gender_id = db.Column(db.Integer, primary_key=True)