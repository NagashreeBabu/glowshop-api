import pytest
import json
from app import create_app, db
from app.models import Product

@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-secret"
    with app.app_context():
        db.create_all()
        p1 = Product(name="Vitamin C Serum", price=999.0, stock=50, category="Serum", skin_type="All skin types", brand="GlowLab", ingredients="Vitamin C", spf=0)
        p2 = Product(name="SPF 50 Sunscreen", price=749.0, stock=30, category="Sunscreen", skin_type="All skin types", brand="SunShield", ingredients="Zinc Oxide", spf=50)
        db.session.add_all([p1, p2])
        db.session.commit()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_get_all_products(client):
    response = client.get("/api/products/")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "products" in data
    assert data["total"] == 2

def test_get_product_by_id(client):
    response = client.get("/api/products/1")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["name"] == "Vitamin C Serum"

def test_filter_by_category(client):
    response = client.get("/api/products/?category=Serum")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["total"] == 1
    assert data["products"][0]["category"] == "Serum"

def test_filter_by_spf(client):
    response = client.get("/api/products/?spf=30")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["total"] == 1

def test_get_categories(client):
    response = client.get("/api/products/categories")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "Serum" in data["categories"]

def test_get_nonexistent_product(client):
    response = client.get("/api/products/9999")
    assert response.status_code == 404
