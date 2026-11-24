
from flask import Blueprint, jsonify, request
from sqlalchemy import text
from extensions import db
from decimal import Decimal, InvalidOperation
from permissions import roles_required
from flask_jwt_extended import get_jwt_identity


orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")



@orders_bp.route("/", methods=["POST"])
@roles_required("Admin", "Advanced User", "Simple User")
def create_order():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"success": False, "message": "Valid JSON required"}), 400

    items = data.get("items")

    if not isinstance(items, list) or not items:
        return jsonify({"success": False, "message": "Order must contain products"}), 400

    try:
        # Identify the logged-in user from the JWT token
        user_id = int(get_jwt_identity())

        # Find this user's client profile
        client = db.session.execute(
            text("""
                SELECT client_id
                FROM clients
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        ).mappings().first()

        if not client:
            return jsonify({
                "success": False,
                "message": "Customer profile not found. Please create your customer profile first."
            }), 400

        client_id = client["client_id"]

        total_amount = Decimal("0.00")
        order_items = []

        for item in items:
            product_id = int(item["product_id"])
            quantity = int(item["quantity"])

            if product_id <= 0 or quantity <= 0:
                raise ValueError()

            product = db.session.execute(
                text("""
                    SELECT product_id, price
                    FROM products
                    WHERE product_id = :id AND is_active = 1
                """),
                {"id": product_id}
            ).mappings().first()

            if not product:
                return jsonify({
                    "success": False,
                    "message": f"Product {product_id} not found"
                }), 404

            unit_price = Decimal(str(product["price"]))
            total_amount += unit_price * quantity

            order_items.append({
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": unit_price
            })

        # Create order for the authenticated user's client profile
        result = db.session.execute(
            text("""
                INSERT INTO orders
                (client_id, order_date, status, total_amount)
                VALUES (:client_id, NOW(), 'pending', :total_amount)
            """),
            {
                "client_id": client_id,
                "total_amount": total_amount
            }
        )

        order_id = result.lastrowid

        for item in order_items:
            db.session.execute(
                text("""
                    INSERT INTO order_items
                    (order_id, product_id, quantity, unit_price)
                    VALUES (:order_id, :product_id, :quantity, :unit_price)
                """),
                {
                    "order_id": order_id,
                    **item
                }
            )

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Order created successfully",
            "order_id": order_id,
            "client_id": client_id,
            "status": "pending",
            "total_amount": str(total_amount)
        }), 201

    except (ValueError, TypeError, KeyError, InvalidOperation):
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Invalid order data"
        }), 400

    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Could not create order"
        }), 500




@orders_bp.route("/", methods=["GET"])
@roles_required("Admin", "Advanced User")
def get_orders():
    orders = db.session.execute(
        text("""
            SELECT
                o.order_id,
                o.client_id,
                o.order_date,
                o.status,
                o.total_amount,
                c.first_name,
                c.last_name,
                c.phone,
                c.city,
                u.username,
                u.email
            FROM orders o
            LEFT JOIN clients c ON o.client_id = c.client_id
            LEFT JOIN users u ON c.user_id = u.user_id
            ORDER BY o.order_date DESC
        """)
    ).mappings().all()

    order_list = []

    for order in orders:
        items = db.session.execute(
            text("""
                SELECT
                    oi.order_item_id,
                    oi.product_id,
                    p.name AS product_name,
                    oi.quantity,
                    oi.unit_price,
                    (oi.quantity * oi.unit_price) AS subtotal
                FROM order_items oi
                LEFT JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = :order_id
            """),
            {"order_id": order["order_id"]}
        ).mappings().all()

        order_list.append({
            "order_id": order["order_id"],
            "client_id": order["client_id"],
            "customer_name": (
                f"{order['first_name']} {order['last_name']}"
                if order["first_name"] else "Unknown Customer"
            ),
            "username": order["username"],
            "email": order["email"],
            "phone": order["phone"],
            "city": order["city"],
            "order_date": str(order["order_date"]),
            "status": order["status"],
            "total_amount": float(order["total_amount"]),
            "items": [
                {
                    "order_item_id": item["order_item_id"],
                    "product_id": item["product_id"],
                    "product_name": item["product_name"] or "Deleted Product",
                    "quantity": item["quantity"],
                    "unit_price": float(item["unit_price"]),
                    "subtotal": float(item["subtotal"])
                }
                for item in items
            ]
        })

    return jsonify({
        "success": True,
        "count": len(order_list),
        "orders": order_list
    }), 200



@orders_bp.route("/<int:order_id>/confirm", methods=["PUT"])
@roles_required("Admin", "Advanced User")
def confirm_order(order_id):
    try:
        # Lock the order while confirming
        order = db.session.execute(
            text("""
                SELECT order_id, status
                FROM orders
                WHERE order_id = :id
                FOR UPDATE
            """),
            {"id": order_id}
        ).mappings().first()

        if not order:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": "Order not found"
            }), 404

        if order["status"] != "pending":
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": "Only pending orders can be confirmed"
            }), 400

        # Group quantities in case the same product appears more than once
        items = db.session.execute(
            text("""
                SELECT product_id, SUM(quantity) AS quantity
                FROM order_items
                WHERE order_id = :id
                GROUP BY product_id
            """),
            {"id": order_id}
        ).mappings().all()

        for item in items:
            # Lock the product row so simultaneous confirmations
            # cannot both use the same available stock
            stock = db.session.execute(
                text("""
                    SELECT
                        p.initial_quantity -
                        COALESCE((
                            SELECT SUM(oi.quantity)
                            FROM order_items oi
                            JOIN orders o ON oi.order_id = o.order_id
                            WHERE oi.product_id = p.product_id
                            AND o.status IN (
                                'confirmed',
                                'processing',
                                'shipped',
                                'delivered'
                            )
                        ), 0) AS available_quantity
                    FROM products p
                    WHERE p.product_id = :product_id
                    FOR UPDATE
                """),
                {"product_id": item["product_id"]}
            ).mappings().first()

            if not stock or stock["available_quantity"] < item["quantity"]:
                db.session.rollback()
                return jsonify({
                    "success": False,
                    "message": (
                        f"Insufficient stock for product "
                        f"{item['product_id']}"
                    )
                }), 400

        # Confirm the order
        db.session.execute(
            text("""
                UPDATE orders
                SET status = 'confirmed'
                WHERE order_id = :id
            """),
            {"id": order_id}
        )

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Order confirmed successfully",
            "order_id": order_id,
            "status": "confirmed"
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Could not confirm order"
        }), 500


@orders_bp.route("/<int:order_id>/cancel", methods=["PUT"])
@roles_required("Admin", "Advanced User")
def cancel_order(order_id):
    try:
        order = db.session.execute(
            text("""
                SELECT order_id, status
                FROM orders
                WHERE order_id = :id
                FOR UPDATE
            """),
            {"id": order_id}
        ).mappings().first()

        if not order:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": "Order not found"
            }), 404

        if order["status"] not in ["pending", "confirmed"]:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": "This order cannot be cancelled"
            }), 400

        db.session.execute(
            text("""
                UPDATE orders
                SET status = 'cancelled'
                WHERE order_id = :id
            """),
            {"id": order_id}
        )

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Order cancelled successfully",
            "order_id": order_id,
            "status": "cancelled"
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Could not cancel order"
        }), 500



@orders_bp.route("/<int:order_id>/status", methods=["PUT"])
@roles_required("Admin", "Advanced User")
def update_order_status(order_id):
    data = request.get_json() or {}
    new_status = data.get("status")

    allowed_transitions = {
        "confirmed": ["processing"],
        "processing": ["shipped"],
        "shipped": ["delivered"]
    }

    if new_status not in ["processing", "shipped", "delivered"]:
        return jsonify({
            "success": False,
            "message": "Invalid status"
        }), 400

    try:
        order = db.session.execute(
            text("SELECT status FROM orders WHERE order_id = :id"),
            {"id": order_id}
        ).mappings().first()

        if not order:
            return jsonify({
                "success": False,
                "message": "Order not found"
            }), 404

        current_status = order["status"]

        if new_status not in allowed_transitions.get(current_status, []):
            return jsonify({
                "success": False,
                "message": f"Cannot change status from {current_status} to {new_status}"
            }), 400

        db.session.execute(
            text("""
                UPDATE orders
                SET status = :status
                WHERE order_id = :id
            """),
            {"status": new_status, "id": order_id}
        )

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Order status updated successfully",
            "order_id": order_id,
            "status": new_status
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@orders_bp.route("/my-orders", methods=["GET"])
@roles_required("Admin", "Advanced User", "Simple User")
def get_my_orders():
    try:
        user_id = int(get_jwt_identity())

        # Find the logged-in user's customer profile
        client = db.session.execute(
            text("""
                SELECT client_id
                FROM clients
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        ).mappings().first()

        if not client:
            return jsonify({
                "success": False,
                "message": "Customer profile not found"
            }), 404

        client_id = client["client_id"]

        # Get only this customer's orders
        orders = db.session.execute(
            text("""
                SELECT
                    order_id,
                    order_date,
                    status,
                    total_amount
                FROM orders
                WHERE client_id = :client_id
                ORDER BY order_date DESC
            """),
            {"client_id": client_id}
        ).mappings().all()

        result = []

        for order in orders:
            # Get products belonging to this order
            items = db.session.execute(
                text("""
                    SELECT
                        p.name AS product_name,
                        oi.quantity,
                        oi.unit_price
                    FROM order_items oi
                    JOIN products p ON oi.product_id = p.product_id
                    WHERE oi.order_id = :order_id
                """),
                {"order_id": order["order_id"]}
            ).mappings().all()

            result.append({
                "order_id": order["order_id"],
                "order_date": str(order["order_date"]),
                "status": order["status"],
                "total_amount": float(order["total_amount"]),
                "items": [
                    {
                        "product_name": item["product_name"],
                        "quantity": item["quantity"],
                        "unit_price": float(item["unit_price"])
                    }
                    for item in items
                ]
            })

        return jsonify({
            "success": True,
            "count": len(result),
            "orders": result
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Could not retrieve your orders"
        }), 500
