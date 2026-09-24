from flask import Flask
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

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(products_bp, url_prefix="/api/products")
    app.register_blueprint(cart_bp, url_prefix="/api/cart")
    app.register_blueprint(orders_bp, url_prefix="/api/orders")
    app.register_blueprint(reviews_bp, url_prefix="/api/reviews")

    with app.app_context():
        db.create_all()
        seed_products()

    return app


def seed_products():
    from app.models import Product
    if Product.query.first():
        return

    products = [
        Product(name="Vitamin C Brightening Serum", description="Fades dark spots and evens skin tone with 15% Vitamin C, Niacinamide and Hyaluronic Acid.", price=1299.00, stock=50, category="Serum", skin_type="All skin types", brand="GlowLab", ingredients="Vitamin C 15%, Niacinamide, Hyaluronic Acid", spf=0),
        Product(name="Hydrating Gel Moisturiser", description="Lightweight oil-free gel that provides 72-hour hydration without clogging pores.", price=899.00, stock=80, category="Moisturiser", skin_type="Oily, Combination", brand="AquaGlow", ingredients="Hyaluronic Acid, Aloe Vera, Glycerin", spf=0),
        Product(name="Gentle Foaming Cleanser", description="Sulphate-free foaming cleanser that removes makeup and impurities without stripping skin.", price=549.00, stock=100, category="Cleanser", skin_type="All skin types", brand="PureClean", ingredients="Aloe Vera, Chamomile, Green Tea Extract", spf=0),
        Product(name="SPF 50 Sunscreen Fluid", description="Lightweight daily sunscreen with broad spectrum UVA/UVB protection. Non-greasy finish.", price=749.00, stock=120, category="Sunscreen", skin_type="All skin types", brand="SunShield", ingredients="Zinc Oxide, Titanium Dioxide, Vitamin E", spf=50),
        Product(name="Retinol Night Repair Cream", description="0.3% Retinol anti-ageing cream that reduces fine lines and improves skin texture overnight.", price=1599.00, stock=40, category="Night Cream", skin_type="Normal, Dry, Combination", brand="YouthRx", ingredients="Retinol 0.3%, Peptides, Shea Butter, Vitamin E", spf=0),
        Product(name="Niacinamide 10% Pore Minimiser", description="10% Niacinamide serum that minimises pores, controls oil and reduces blemishes.", price=799.00, stock=90, category="Serum", skin_type="Oily, Combination, Acne-prone", brand="ClearSkin", ingredients="Niacinamide 10%, Zinc PCA, Hyaluronic Acid", spf=0),
        Product(name="Rose Hip Facial Oil", description="Cold-pressed rosehip seed oil rich in Vitamin A and C for intense nourishment and radiance.", price=1099.00, stock=35, category="Face Oil", skin_type="Dry, Mature", brand="NaturGlow", ingredients="Rosa Canina Seed Oil, Vitamin A, Vitamin C, Omega 6", spf=0),
        Product(name="Salicylic Acid BHA Toner", description="2% Salicylic Acid toner that unclogs pores, removes dead skin cells and prevents breakouts.", price=649.00, stock=75, category="Toner", skin_type="Oily, Acne-prone", brand="ClearSkin", ingredients="Salicylic Acid 2%, Witch Hazel, Aloe Vera", spf=0),
        Product(name="Under Eye Peptide Cream", description="Reduces dark circles, puffiness and fine lines around the delicate eye area with Caffeine and Peptides.", price=1199.00, stock=45, category="Eye Cream", skin_type="All skin types", brand="EyeLift", ingredients="Caffeine, Peptides, Vitamin K, Hyaluronic Acid", spf=0),
        Product(name="Kaolin Clay Detox Mask", description="Detoxifying clay mask that draws out impurities, excess oil and minimises pores in 15 minutes.", price=699.00, stock=60, category="Mask", skin_type="Oily, Combination, Acne-prone", brand="PureClay", ingredients="Kaolin Clay, Bentonite Clay, Tea Tree Oil, Charcoal", spf=0),
    ]
    from app import db
    db.session.bulk_save_objects(products)
    db.session.commit()
    print("Skincare products seeded successfully!")
