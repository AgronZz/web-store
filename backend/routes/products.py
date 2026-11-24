
from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from models.product import Product
from extensions import db
from models.product import Product
from sqlalchemy import text
from sqlalchemy import exists
from permissions import roles_required

products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/api/products"
)


# READ ALL PRODUCTS
@products_bp.route("/", methods=["GET"])
def get_products():

    products = Product.query.filter_by(is_active=True).all()

    return jsonify({
        "success": True,
        "count": len(products),
        "products": [product.to_dict() for product in products]
    }), 200


# READ PRODUCT BY ID
@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):

    product = Product.query.filter_by(
        product_id=product_id,
        is_active=True
    ).first()

    if not product:
        return jsonify({
            "success": False,
            "message": "Product not found"
        }), 404

    return jsonify({
        "success": True,
        "product": product.to_dict()
    }), 200


# CREATE PRODUCT
@products_bp.route("/", methods=["POST"])
@roles_required("Admin", "Advanced User")
def create_product():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "A valid JSON object is required"
        }), 400

    required_fields = [
        "name",
        "price",
        "initial_quantity",
        "category_id",
        "brand_id",
        "gender_id"
    ]

    missing_fields = [
        field for field in required_fields
        if field not in data
    ]

    if missing_fields:
        return jsonify({
            "success": False,
            "message": "Missing required fields",
            "missing_fields": missing_fields
        }), 400

    try:
        price = float(data["price"])
        quantity = int(data["initial_quantity"])
        category_id = int(data["category_id"])
        brand_id = int(data["brand_id"])
        gender_id = int(data["gender_id"])

        if price < 0 or quantity < 0:
            raise ValueError()

        if any(value <= 0 for value in [
            category_id, brand_id, gender_id
        ]):
            raise ValueError()

        if not str(data["name"]).strip():
            raise ValueError()

    except (ValueError, TypeError, OverflowError):
        return jsonify({
            "success": False,
            "message": "Invalid product data"
        }), 400

    if not isinstance(data["name"], str):
        return jsonify({
            "success": False,
            "message": "Product name must be text"
        }), 400

    product = Product(
        name=data["name"].strip(),
        description=data.get("description"),
        price=price,
        initial_quantity=quantity,
        category_id=category_id,
        brand_id=brand_id,
        gender_id=gender_id
    )

    try:
        db.session.add(product)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Product created successfully",
            "product": product.to_dict()
        }), 201

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Invalid category, brand, or gender ID"
        }), 400


# UPDATE PRODUCT
@products_bp.route("/<int:product_id>", methods=["PUT"])
@roles_required("Admin", "Advanced User")
def update_product(product_id):

    product = Product.query.filter_by(
        product_id=product_id,
        is_active=True
    ).first()

    if not product:
        return jsonify({
            "success": False,
            "message": "Product not found"
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not data:
        return jsonify({
            "success": False,
            "message": "Provide valid JSON data"
        }), 400

    allowed_fields = [
        "name",
        "description",
        "price",
        "initial_quantity",
        "category_id",
        "brand_id",
        "gender_id"
    ]

    try:
        for field in allowed_fields:
            if field not in data:
                continue

            value = data[field]

            if field == "name":
                if not isinstance(value, str) or not value.strip():
                    raise ValueError()
                value = value.strip()

            elif field == "description":
                if value is not None and not isinstance(value, str):
                    raise ValueError()

            elif field == "price":
                value = float(value)
                if value < 0:
                    raise ValueError()

            elif field in ["initial_quantity", "category_id",
                           "brand_id", "gender_id"]:
                if isinstance(value, bool):
                    raise ValueError()

                integer_value = int(value)

                if integer_value != float(value):
                    raise ValueError()

                if field == "initial_quantity":
                    if integer_value < 0:
                        raise ValueError()
                elif integer_value <= 0:
                    raise ValueError()

                value = integer_value

            setattr(product, field, value)

        if not any(field in data for field in allowed_fields):
            return jsonify({
                "success": False,
                "message": "No valid fields provided for update"
            }), 400

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Product updated successfully",
            "product": product.to_dict()
        }), 200

    except (ValueError, TypeError, OverflowError):
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Invalid product data"
        }), 400

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            "success": False,
            "message": "Invalid category, brand, or gender ID"
        }), 400


# DELETE PRODUCT (SOFT DELETE)
@products_bp.route("/<int:product_id>", methods=["DELETE"])
@roles_required("Admin", "Advanced User")
def delete_product(product_id):

    product = Product.query.filter_by(
        product_id=product_id,
        is_active=True
    ).first()

    if not product:
        return jsonify({
            "success": False,
            "message": "Product not found"
        }), 404

    product.is_active = False
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Product deleted successfully"
    }), 200



@products_bp.route("/search", methods=["GET"])
def search_products():
    query = Product.query.filter_by(is_active=True)

    # Search by product name
    name = request.args.get("name")
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))

    # Filter by category
    category_id = request.args.get("category_id")
    if category_id:
        try:
            query = query.filter(Product.category_id == int(category_id))
        except ValueError:
            return jsonify({"success": False, "message": "Invalid category ID"}), 400

    # Filter by brand
    brand_id = request.args.get("brand_id")
    if brand_id:
        try:
            query = query.filter(Product.brand_id == int(brand_id))
        except ValueError:
            return jsonify({"success": False, "message": "Invalid brand ID"}), 400

    # Filter by gender
    gender_id = request.args.get("gender_id")
    if gender_id:
        try:
            query = query.filter(Product.gender_id == int(gender_id))
        except ValueError:
            return jsonify({"success": False, "message": "Invalid gender ID"}), 400

    # Filter by price
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")

    try:
        if min_price is not None:
            min_price = float(min_price)
            if min_price < 0:
                raise ValueError()
            query = query.filter(Product.price >= min_price)

        if max_price is not None:
            max_price = float(max_price)
            if max_price < 0:
                raise ValueError()
            query = query.filter(Product.price <= max_price)

        if min_price is not None and max_price is not None:
            if min_price > max_price:
                raise ValueError()

    except (ValueError, TypeError):
        return jsonify({"success": False, "message": "Invalid price range"}), 400

    # Filter by size
    size_id = request.args.get("size_id")
    if size_id:
        try:
            size_id = int(size_id)
            product_ids = db.session.execute(
                text("""
                    SELECT product_id
                    FROM product_sizes
                    WHERE size_id = :size_id
                """),
                {"size_id": size_id}
            ).scalars().all()

            query = query.filter(Product.product_id.in_(product_ids))

        except ValueError:
            return jsonify({"success": False, "message": "Invalid size ID"}), 400

    # Filter by color name
    color_name = request.args.get("color_name")
    if color_name:
        product_ids = db.session.execute(
            text("""
                SELECT pc.product_id
                FROM product_colors pc
                JOIN colors c ON pc.color_id = c.color_id
                WHERE LOWER(c.color_name) = LOWER(:color_name)
            """),
            {"color_name": color_name.strip()}
        ).scalars().all()

        query = query.filter(Product.product_id.in_(product_ids))

    # Return matching products
    products = query.all()

    return jsonify({
        "success": True,
        "count": len(products),
        "products": [product.to_dict() for product in products]
    }), 200
