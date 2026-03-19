import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"
