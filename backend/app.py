
from flask import Flask, jsonify
from flask_cors import CORS

from config import Config
from extensions import db
from routes import products_bp, orders_bp, reports_bp, users_bp
from models import Product
from flask_jwt_extended import JWTManager



def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)
    jwt = JWTManager(app)

    # Enable communication with React
    CORS(app)

    # Initialize MySQL connection
    db.init_app(app)

    # Register API routes
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(users_bp)

    # Home endpoint
    @app.route("/", methods=["GET"])
    def home():
        return jsonify({
            "message": "Web Store API is running!",
            "status": "success"
        }), 200

    # Database connection test
    @app.route("/api/health", methods=["GET"])
    def health():
        try:
            with db.engine.connect() as connection:
                connection.exec_driver_sql("SELECT 1")

            return jsonify({
                "success": True,
                "message": "MySQL connection successful!"
            }), 200

        except Exception as error:
            app.logger.exception("Database connection failed")

            return jsonify({
                "success": False,
                "message": "Database connection failed"
            }), 500

    return app


app = create_app()



if __name__ == "__main__":
    app.run(debug=True, port=5000)
