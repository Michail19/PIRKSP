import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///local.db")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    APP_ENV = os.getenv("APP_ENV", "local")
    APP_VERSION = os.getenv("APP_VERSION", "dev")
    SERVICE_NAME = os.getenv("SERVICE_NAME", "pirksp")

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    SHUTDOWN_TIMEOUT = int(os.getenv("SHUTDOWN_TIMEOUT", "10"))
