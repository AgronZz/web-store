
from flask import Blueprint, jsonify, request
from sqlalchemy import text
from datetime import datetime, date
from extensions import db
from permissions import roles_required

reports_bp = Blueprint(
    "reports",
    __name__,
    url_prefix="/api/reports"
)

# Only these order statuses count as revenue.
VALID_STATUSES = "'confirmed', 'processing', 'shipped', 'delivered'"


# 1. DAILY EARNINGS
@reports_bp.route("/daily-earnings", methods=["GET"])
@roles_required("Admin", "Advanced User")
def daily_earnings():
    date_value = request.args.get("date")

    try:
        report_date = (
            datetime.strptime(date_value, "%Y-%m-%d").date()
            if date_value else date.today()
        )
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid date. Use YYYY-MM-DD."
        }), 400

    result = db.session.execute(
        text(f"""
            SELECT
                COUNT(*) AS total_orders,
                COALESCE(SUM(total_amount), 0) AS total_earnings
            FROM orders
            WHERE DATE(order_date) = :report_date
            AND status IN ({VALID_STATUSES})
        """),
        {"report_date": report_date}
    ).mappings().first()

    return jsonify({
        "success": True,
        "date": str(report_date),
        "total_orders": result["total_orders"],
        "total_earnings": float(result["total_earnings"])
    }), 200


# 2. MONTHLY EARNINGS
@reports_bp.route("/monthly-earnings", methods=["GET"])
@roles_required("Admin", "Advanced User")
def monthly_earnings():
    try:
        year = int(request.args.get("year", date.today().year))
        month = int(request.args.get("month", date.today().month))

        if year < 2000 or month < 1 or month > 12:
            raise ValueError()

    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid year or month."
        }), 400

    result = db.session.execute(
        text(f"""
            SELECT
                COUNT(*) AS total_orders,
                COALESCE(SUM(total_amount), 0) AS total_earnings
            FROM orders
            WHERE YEAR(order_date) = :year
            AND MONTH(order_date) = :month
            AND status IN ({VALID_STATUSES})
        """),
        {"year": year, "month": month}
    ).mappings().first()

    return jsonify({
        "success": True,
        "year": year,
        "month": month,
        "total_orders": result["total_orders"],
        "total_earnings": float(result["total_earnings"])
    }), 200


# 3. TOP-SELLING PRODUCTS
@reports_bp.route("/top-products", methods=["GET"])
@roles_required("Admin", "Advanced User")
def top_products():
    try:
        limit = int(request.args.get("limit", 10))

        if limit < 1 or limit > 100:
            raise ValueError()

    except ValueError:
        return jsonify({
            "success": False,
            "message": "Limit must be between 1 and 100."
        }), 400

    results = db.session.execute(
        text(f"""
            SELECT
                p.product_id,
                p.name,
                SUM(oi.quantity) AS total_sold,
                SUM(oi.quantity * oi.unit_price) AS total_revenue
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            JOIN products p ON oi.product_id = p.product_id
            WHERE o.status IN ({VALID_STATUSES})
            GROUP BY p.product_id, p.name
            ORDER BY total_sold DESC
            LIMIT :limit
        """),
        {"limit": limit}
    ).mappings().all()

    return jsonify({
        "success": True,
        "count": len(results),
        "top_products": [
            {
                "product_id": row["product_id"],
                "name": row["name"],
                "total_sold": int(row["total_sold"]),
                "total_revenue": float(row["total_revenue"])
            }
            for row in results
        ]
    }), 200
