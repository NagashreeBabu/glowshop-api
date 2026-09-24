from flask import Blueprint, request, jsonify
from app import db
from app.models import Order, OrderItem, CartItem, Product
from flask_jwt_extended import jwt_required, get_jwt_identity

orders_bp = Blueprint("orders", __name__)

@orders_bp.route("/", methods=["POST"])
@jwt_required()
def place_order():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    address = data.get("address", "")
    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({"error": "Your cart is empty"}), 400
    total = 0
    order_items = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if not product:
            continue
        if product.stock < item.quantity:
            return jsonify({"error": "Not enough stock"}), 400
        total += product.price * item.quantity
        order_items.append((product, item.quantity, product.price))
    order = Order(user_id=user_id, total=round(total, 2), address=address, status="confirmed")
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
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    result = []
    for order in orders:
        items = []
        for oi in order.items:
            p = Product.query.get(oi.product_id)
            items.append({"product_name": p.name if p else "N/A", "quantity": oi.quantity, "price": oi.price})
        result.append({"order_id": order.id, "total": order.total, "status": order.status, "items": items})
    return jsonify({"orders": result}), 200

@orders_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404
    items = []
    for oi in order.items:
        p = Product.query.get(oi.product_id)
        items.append({"product_name": p.name if p else "N/A", "quantity": oi.quantity, "price": oi.price})
    return jsonify({"order_id": order.id, "total": order.total, "status": order.status, "items": items}), 200