import time
import redis
from flask import Flask, jsonify
from flask_session import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from config import Config
from app.db.database import db
from app.routes.user_routes import user_bp

session_ext = Session()

def wait_for_db(app, retries=10, delay=3):
    for attempt in range(1, retries + 1):
        try:
            with app.app_context():
                with db.engine.connect() as connection:
                    connection.execute(text("SELECT 1"))
            print("Database is ready.")
            return
        except OperationalError:
            print(f"Database is not ready yet... attempt {attempt}/{retries}")
            time.sleep(delay)
    raise RuntimeError("Database is not available after several retries.")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = Config.SECRET_KEY

    db.init_app(app)

    app.config["SESSION_REDIS"] = redis.from_url(Config.REDIS_URL)
    session_ext.init_app(app)

    with app.app_context():
        from app.models.user import User
        wait_for_db(app)
        db.create_all()

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "message": "API работает",
            "env": app.config["APP_ENV"],
            "version": app.config["APP_VERSION"]
        })

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    app.register_blueprint(user_bp)
    return app
