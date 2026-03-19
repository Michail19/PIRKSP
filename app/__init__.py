from flask import Flask, jsonify
from config import Config
from app.db.database import db
from app.routes.user_routes import user_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        from app.models.user import User
        db.create_all()

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "message": "API работает",
            "available_routes": [
                "GET /",
                "GET /health",
                "GET /users",
                "POST /users"
            ]
        })

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    app.register_blueprint(user_bp)
    return app
