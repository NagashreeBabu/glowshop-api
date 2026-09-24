orders_code = """from flask import Blueprint, request, jsonify
from app import db
from app.models import Order, OrderItem, CartItem, Product
from flask_jwt_extended import jwt_required, get_jwt_identity

orders_bp = Blueprint("orders", __name__)

@orders_bp.route("/", methods=["POST"])
@jwt_required()
def place_order():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400
    total = 0
    order_items = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product:
            total += product.price * item.quantity
            order_items.append((product, item.quantity, product.price))
    order = Order(user_id=user_id, total=round(total, 2), status="confirmed")
    db.session.add(order)
    db.session.flush()
    for product, quantity, price in order_items:
        db.session.add(OrderItem(order_id=order.id, product_id=product.id, quantity=quantity, price=price))
        product.stock -= quantity
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({"message": "Order placed!", "order_id": order.id, "total": order.total}), 201

@orders_bp.route("/", methods=["GET"])
@jwt_required()
def get_orders():
    user_id = int(get_jwt_identity())
    orders = Order.query.filter_by(user_id=user_id).all()
    result = [{"order_id": o.id, "total": o.total, "status": o.status} for o in orders]
    return jsonify({"orders": result}), 200
"""

init_code = """from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from config import Config

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    jwt.init_app(app)
    from app.routes.auth import auth_bp
    from app.routes.products import products_bp
    from app.routes.cart import cart_bp
    from app.routes.orders import orders_bp
    from app.routes.reviews import reviews_bp