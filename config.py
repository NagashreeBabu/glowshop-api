import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "skincare-secret-key-2024")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///skincare.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "skincare-jwt-secret-2024")
