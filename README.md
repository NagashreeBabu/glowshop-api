# GlowShop — Skincare E-Commerce REST API

A Python Flask REST API for a skincare e-commerce platform. Built as a portfolio project demonstrating backend development skills including JWT authentication, SQLAlchemy ORM, RESTful API design, and automated testing with pytest.

## Tech Stack
- **Python 3.13** — Programming language
- **Flask** — Web framework
- **SQLAlchemy** — ORM for database operations
- **SQLite** — Database (development)
- **JWT** — Authentication tokens
- **bcrypt** — Password encryption
- **pytest** — Automated testing

## Features
- User registration and login with JWT authentication
- User skin type profile for personalised recommendations
- Full product CRUD with category, brand, skin type, SPF filters
- Search products by name, description, or ingredients
- Personalised product recommendations based on skin type
- Shopping cart management (add, update, remove, clear)
- Order placement with stock validation
- Product reviews and ratings system
- 10 pre-seeded skincare products on first run

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python run.py
```

Server runs at: http://127.0.0.1:5000

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/auth/register | Register new user |
| POST | /api/auth/login | Login, returns JWT token |
| GET | /api/auth/profile | View profile (auth required) |
| PUT | /api/auth/profile | Update skin type/concerns |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/products/ | List all products |
| GET | /api/products/?category=Serum | Filter by category |
| GET | /api/products/?skin_type=Oily | Filter by skin type |
| GET | /api/products/?search=vitamin | Search products |
| GET | /api/products/?spf=30 | Filter by SPF |
| GET | /api/products/recommend | Personalised recommendations |
| GET | /api/products/categories | List all categories |
| POST | /api/products/ | Add product (auth) |

### Cart
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/cart/ | View cart with total |
| POST | /api/cart/ | Add item to cart |
| PUT | /api/cart/:id | Update quantity |
| DELETE | /api/cart/:id | Remove item |
| DELETE | /api/cart/clear | Clear entire cart |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/orders/ | Place order |
| GET | /api/orders/ | Order history |
| GET | /api/orders/:id | Single order detail |

### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/reviews/:product_id | Get product reviews |
| POST | /api/reviews/:product_id | Add review (auth) |
| DELETE | /api/reviews/:id | Delete review (auth) |

## Running Tests

```bash
pytest -v
```

## Developer
Built by [Your Name] — transitioning from QA automation to Python backend development.
