from extensions import db

class Brand(db.Model):
    __tablename__ = "brands"

    brand_id = db.Column(db.Integer, primary_key=True)