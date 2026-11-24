
from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

from extensions import db
from models.user import User
from models.role import Role

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from models.user import User

from permissions import roles_required

users_bp = Blueprint(
    "users",
    __name__,
    url_prefix="/api/users"
)


# GET ALL USERS
@users_bp.route("/", methods=["GET"])
@roles_required("Admin")
def get_users():
    users = User.query.all()

    return jsonify({
        "success": True,
        "count": len(users),
        "users": [user.to_dict() for user in users]
    }), 200


# GET ONE USER
@users_bp.route("/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    return jsonify({
        "success": True,
        "user": user.to_dict()
    }), 200


# CREATE USER
@users_bp.route("/", methods=["POST"])
@roles_required("Admin")
def create_user():
    data = request.get_json() or {}

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role_id = data.get("role_id")

    if not all([username, email, password, role_id]):
        return jsonify({
            "success": False,
            "message": "Username, email, password and role_id are required"
        }), 400

    username = username.strip()
    email = email.strip().lower()

    if not username or not email or len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Username and email cannot be empty. Password must have at least 8 characters."
        }), 400

    try:
        role_id = int(role_id)
    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Invalid role_id"
        }), 400

    role = db.session.get(Role, role_id)

    if not role:
        return jsonify({
            "success": False,
            "message": "Role not found"
        }), 404

    existing_user = User.query.filter(
        (User.username == username) | (User.email == email)
    ).first()

    if existing_user:
        return jsonify({
            "success": False,
            "message": "Username or email already exists"
        }), 409

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(
        password,
        method="pbkdf2:sha256"),
        role_id=role_id
    )

    try:
        db.session.add(user)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "User created successfully",
            "user": user.to_dict()
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Username or email already exists"
        }), 409


# UPDATE USER
@users_bp.route("/<int:user_id>", methods=["PUT"])
@roles_required("Admin")
def update_user(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    data = request.get_json() or {}

    if "username" in data:
        username = data["username"].strip()

        if not username:
            return jsonify({
                "success": False,
                "message": "Username cannot be empty"
            }), 400

        user.username = username

    if "email" in data:
        email = data["email"].strip().lower()

        if not email:
            return jsonify({
                "success": False,
                "message": "Email cannot be empty"
            }), 400

        user.email = email

    if "role_id" in data:
        try:
            role_id = int(data["role_id"])
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Invalid role_id"
            }), 400

        if not db.session.get(Role, role_id):
            return jsonify({
                "success": False,
                "message": "Role not found"
            }), 404

        user.role_id = role_id

    if "password" in data:
        password = data["password"]

        if not isinstance(password, str) or len(password) < 8:
            return jsonify({
                "success": False,
                "message": "Password must have at least 8 characters"
            }), 400

        user.password_hash = generate_password_hash(
        password,
        method="pbkdf2:sha256"
        )

    try:
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "User updated successfully",
            "user": user.to_dict()
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Username or email already exists"
        }), 409


# DELETE USER
@users_bp.route("/<int:user_id>", methods=["DELETE"])
@roles_required("Admin")
def delete_user(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({
            "success": False,
            "message": "User not found"
        }), 404

    try:
        db.session.delete(user)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "User deleted successfully"
        }), 200

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": "Cannot delete this user because it is referenced by other records"
        }), 409



@users_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    user = User.query.filter_by(email=email.strip()).first()

    if not user:
        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    if not check_password_hash(user.password_hash, password):
        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

    access_token = create_access_token(
        identity=str(user.user_id),
        additional_claims={
            "role": user.role.role_name
        }
    )

    return jsonify({
        "success": True,
        "message": "Login successful",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200
