from flask import Blueprint, request, jsonify
from app import db
from app.models import Product
from flask_jwt_extended import jwt_required

products_bp = Blueprint("products", __name__)

@products_bp.route("/", methods=["GET"])
def get_products():
    category = request.args.get("category")
    skin_type = request.args.get("skin_type")
    brand = request.args.get("brand")
    search = request.args.get("search")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    spf = request.args.get("spf")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = Product.query.filter_by(is_active=True)

    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if skin_type:
        query = query.filter(Product.skin_type.ilike(f"%{skin_type}%"))
    if brand:
        query = query.filter(Product.brand.ilike(f"%{brand}%"))
    if search:
        query = query.filter(
            db.or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%"),
                Product.ingredients.ilike(f"%{search}%")
            )
        )
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if spf:
        query = query.filter(Product.spf >= int(spf))

    paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "products": [p.to_dict() for p in paginated.items],
        "total": paginated.total,
        "page": page,
        "pages": paginated.pages,
        "per_page": per_page
    }), 200

@products_bp.route("/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    return jsonify(product.to_dict()), 200

@products_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = db.session.query(Product.category).distinct().all()
    return jsonify({"categories": [c[0] for c in categories if c[0]]}), 200

@products_bp.route("/brands", methods=["GET"])
def get_brands():
    brands = db.session.query(Product.brand).distinct().all()
    return jsonify({"brands": [b[0] for b in brands if b[0]]}), 200

@products_bp.route("/recommend", methods=["GET"])
@jwt_required()
def recommend():
    from flask_jwt_extended import get_jwt_identity
    from app.models import User
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))
    if not user or not user.skin_type:
        return jsonify({"message": "Update your skin type in profile for recommendations", "products": []}), 200
    products = Product.query.filter(
        Product.skin_type.ilike(f"%{user.skin_type}%"),
        Product.is_active == True
    ).limit(5).all()
    return jsonify({
        "message": f"Recommended for {user.skin_type} skin",
        "products": [p.to_dict() for p in products]
    }), 200

@products_bp.route("/", methods=["POST"])
@jwt_required()
def add_product():
    data = request.get_json()
    if not data.get("name") or not data.get("price"):
        return jsonify({"error": "name and price are required"}), 400
    product = Product(
        name=data["name"],
        description=data.get("description", ""),
        price=data["price"],
        stock=data.get("stock", 0),
        category=data.get("category", ""),
        skin_type=data.get("skin_type", ""),
        brand=data.get("brand", ""),
        ingredients=data.get("ingredients", ""),
        spf=data.get("spf", 0)
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({"message": "Product added", "product": product.to_dict()}), 201

@products_bp.route("/<int:product_id>", methods=["PUT"])
@jwt_required()
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    data = request.get_json()
    for field in ["name", "description", "price", "stock", "category", "skin_type", "brand", "ingredients", "spf"]:
        if field in data:
            setattr(product, field, data[field])
    db.session.commit()
    return jsonify({"message": "Product updated", "product": product.to_dict()}), 200

@products_bp.route("/<int:product_id>", methods=["DELETE"])
@jwt_required()
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = False
    db.session.commit()
    return jsonify({"message": f"{product.name} removed from store"}), 200
