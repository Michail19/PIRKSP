import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///local.db")

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
