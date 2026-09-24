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
            return jsonify({"error": f"Sorry, {product.name} only has {product.stock} units left in stock"}), 400
        subtotal = product.price * item.quantity
        total += subtotal
        order_items.append((product, item.quantity, product.price))

    order = Order(user_id=user_id, total=round(total, 2), address=address, status="confirmed")
    db.session.add(order)
    db.session.flush()

    for product, quantity, price in order_items:
        order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=quantity, price=price)
        db.session.add(order_item)
        product.stock -= quantity

    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    return jsonify({
        "message": "Order placed successfully! Your skincare is on the way.",
        "order_id": order.id,
        "total": order.total,
        "status": order.status,
        "items_ordered": len(order_items)
    }), 201

@orders_bp.route("/", methods=["GET"])
@jwt_required()
def get_orders():
    user_id = int(get_jwt_identity())
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    result = []
    for order in orders:
        items = []
        for oi in order.items:
            product = Product.query.get(oi.product_id)
            items.append({
                "product_name": product.name if product else "Product unavailable",
                "brand": product.brand if product else "",
                "quantity": oi.quantity,
                "price": oi.price,
                "subtotal": oi.price * oi.quantity
            })
        result.append({
            "order_id": order.id,
            "total": order.total,
            "status": order.status,
            "address": order.address,
            "date": order.created_at.strftime("%d %b %Y, %I:%M %p"),
            "items": items
        })
    return jsonify({"orders": result, "total_orders": len(result)}), 200

@orders_bp.route("/<int:order_id>", methods=["GET"])
@jwt_required()
def get_order(order_id):
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()
    if not order:
        return jsonify({"error": "Order not found"}), 404
    items = []
    for oi in order.items:
        product = Product.query.get(oi.product_id)
        items.append({
            "product_name": product.name if product else "Unavailable",
            "brand": product.brand if product else "",
            "quantity": oi.quantity,
            "price": oi.price,
            "subtotal": oi.price * oi.quantity
        })
    return jsonify({
        "order_id": order.id,
        "total": order.total,
        "status": order.status,
        "address": order.address,
        "date": order.created_at.strftime("%d %b %Y"),
        "items": items
    }), 200
