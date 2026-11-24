from sqlalchemy import text
from extensions import db
from datetime import datetime


class Product(db.Model):
    __tablename__ = "products"

    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    initial_quantity = db.Column(db.Integer, nullable=False, default=0)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.category_id"),
        nullable=False
    )

    brand_id = db.Column(
        db.Integer,
        db.ForeignKey("brands.brand_id"),
        nullable=False
    )

    gender_id = db.Column(
        db.Integer,
        db.ForeignKey("genders.gender_id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    is_active = db.Column(db.Boolean, default=True)

    
    def to_dict(self):

        confirmed_quantity = db.session.execute(
            text("""
                SELECT COALESCE(SUM(oi.quantity), 0)
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id
                WHERE oi.product_id = :product_id
                AND o.status IN ('confirmed', 'processing', 'shipped', 'delivered')
            """),
            {"product_id": self.product_id}
        ).scalar()

        confirmed_quantity = int(confirmed_quantity or 0)

        available_quantity = max(
            0,
            self.initial_quantity - confirmed_quantity
        )

        return {
            "product_id": self.product_id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price),
            "initial_quantity": self.initial_quantity,
            "confirmed_order_quantity": confirmed_quantity,
            "available_quantity": available_quantity,
            "category_id": self.category_id,
            "brand_id": self.brand_id,
            "gender_id": self.gender_id,
            "is_active": self.is_active
        }
