from flask import Blueprint, request, jsonify
from app import db
from app.models import Review, Product, Order, OrderItem
from flask_jwt_extended import jwt_required, get_jwt_identity

reviews_bp = Blueprint("reviews", __name__)

@reviews_bp.route("/<int:product_id>", methods=["GET"])
def get_reviews(product_id):
    product = Product.query.get_or_404(product_id)
    reviews = Review.query.filter_by(product_id=product_id).order_by(Review.created_at.desc()).all()
    result = []
    for r in reviews:
        result.append({
            "review_id": r.id,
            "username": r.user.username,
            "rating": r.rating,
            "comment": r.comment,
            "date": r.created_at.strftime("%d %b %Y")
        })
    return jsonify({
        "product": product.name,
        "average_rating": product.average_rating(),
        "total_reviews": len(result),
        "reviews": result
    }), 200

@reviews_bp.route("/<int:product_id>", methods=["POST"])
@jwt_required()
def add_review(product_id):
    user_id = int(get_jwt_identity())
    product = Product.query.get_or_404(product_id)
    data = request.get_json()

    if not data.get("rating"):
        return jsonify({"error": "rating is required (1-5)"}), 400
    if not 1 <= int(data["rating"]) <= 5:
        return jsonify({"error": "rating must be between 1 and 5"}), 400

    existing = Review.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        return jsonify({"error": "You have already reviewed this product"}), 409

    review = Review(
        user_id=user_id,
        product_id=product_id,
        rating=int(data["rating"]),
        comment=data.get("comment", "")
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({"message": f"Thank you for reviewing {product.name}!"}), 201

@reviews_bp.route("/<int:review_id>", methods=["DELETE"])
@jwt_required()
def delete_review(review_id):
    user_id = int(get_jwt_identity())
    review = Review.query.filter_by(id=review_id, user_id=user_id).first()
    if not review:
        return jsonify({"error": "Review not found"}), 404
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted"}), 200
