from flask import Blueprint, request, jsonify
from app import db
from app.models import CartItem, Product
from flask_jwt_extended import jwt_required, get_jwt_identity

cart_bp = Blueprint("cart", __name__)

@cart_bp.route("/", methods=["GET"])
@jwt_required()
def get_cart():
    user_id = int(get_jwt_identity())
    items = CartItem.query.filter_by(user_id=user_id).all()
    cart_items = []
    total = 0
    for item in items:
        product = Product.query.get(item.product_id)
        if product:
            subtotal = product.price * item.quantity
            total += subtotal
            cart_items.append({
                "cart_item_id": item.id,
                "product_id": product.id,
                "name": product.name,
                "brand": product.brand,
                "category": product.category,
                "price": product.price,
                "quantity": item.quantity,
                "subtotal": subtotal
            })
    return jsonify({
        "items": cart_items,
        "item_count": len(cart_items),
        "total": round(total, 2)
    }), 200

@cart_bp.route("/", methods=["POST"])
@jwt_required()
def add_to_cart():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    if not product_id:
        return jsonify({"error": "product_id is required"}), 400

    product = Product.query.get(product_id)
    if not product or not product.is_active:
        return jsonify({"error": "Product not found"}), 404
    if product.stock < quantity:
        return jsonify({"error": f"Only {product.stock} units available in stock"}), 400

    existing = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        existing.quantity += quantity
    else:
        cart_item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({"message": f"{product.name} added to cart"}), 201

@cart_bp.route("/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_cart_item(item_id):
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        return jsonify({"error": "Cart item not found"}), 404
    data = request.get_json()
    quantity = data.get("quantity")
    if quantity and quantity > 0:
        product = Product.query.get(item.product_id)
        if product.stock < quantity:
            return jsonify({"error": f"Only {product.stock} units available"}), 400
        item.quantity = quantity
        db.session.commit()
    return jsonify({"message": "Cart updated"}), 200

@cart_bp.route("/<int:item_id>", methods=["DELETE"])
@jwt_required()
def remove_from_cart(item_id):
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        return jsonify({"error": "Cart item not found"}), 404
    product = Product.query.get(item.product_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f"{product.name} removed from cart"}), 200

@cart_bp.route("/clear", methods=["DELETE"])
@jwt_required()
def clear_cart():
    user_id = int(get_jwt_identity())
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({"message": "Cart cleared"}), 200
