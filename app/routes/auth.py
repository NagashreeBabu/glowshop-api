from flask import Blueprint, request, jsonify
from app import db
from app.models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import bcrypt

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data or not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "username, email and password are required"}), 400
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"error": "Username already taken"}), 409

    hashed = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt())
    user = User(
        username=data["username"],
        email=data["email"],
        password=hashed.decode("utf-8"),
        skin_type=data.get("skin_type", ""),
        skin_concerns=data.get("skin_concerns", "")
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": f"Welcome to GlowShop, {user.username}! Account created successfully."}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "email and password are required"}), 400
    user = User.query.filter_by(email=data["email"]).first()
    if not user or not bcrypt.checkpw(data["password"].encode("utf-8"), user.password.encode("utf-8")):
        return jsonify({"error": "Invalid email or password"}), 401
    token = create_access_token(identity=str(user.id))
    return jsonify({
        "token": token,
        "username": user.username,
        "skin_type": user.skin_type,
        "message": f"Welcome back, {user.username}!"
    }), 200

@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "skin_type": user.skin_type,
        "skin_concerns": user.skin_concerns,
        "member_since": user.created_at.strftime("%B %Y")
    }), 200

@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    data = request.get_json()
    if data.get("skin_type"):
        user.skin_type = data["skin_type"]
    if data.get("skin_concerns"):
        user.skin_concerns = data["skin_concerns"]
    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200
