import time
import uuid
from flask import Flask, jsonify, g, request, session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from config import Config
from app.db.database import db
from app.routes.user_routes import user_bp
from app.logger import setup_logger


def wait_for_db(app, retries=10, delay=3):
    logger = app.logger_json

    for attempt in range(1, retries + 1):
        try:
            with app.app_context():
                with db.engine.connect() as connection:
                    connection.execute(text("SELECT 1"))

            logger.info(
                "database ready",
                extra={"extra_data": {"attempt": attempt}}
            )
            return
        except OperationalError:
            logger.error(
                "database not ready",
                extra={"extra_data": {"attempt": attempt}}
            )
            time.sleep(delay)

    raise RuntimeError("Database is not available after several retries.")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    logger = setup_logger()
    app.logger_json = logger

    db.init_app(app)

    with app.app_context():
        from app.models.user import User
        wait_for_db(app)
        db.create_all()

    @app.before_request
    def before_request():
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        g.start_time = time.time()

        app.logger_json.info(
            "request started",
            extra={
                "request_id": g.request_id,
                "path": request.path,
                "method": request.method,
            }
        )

    @app.after_request
    def after_request(response):
        duration_ms = round((time.time() - g.start_time) * 1000, 2)

        response.headers["X-Request-ID"] = g.request_id

        app.logger_json.info(
            "request finished",
            extra={
                "request_id": g.request_id,
                "path": request.path,
                "method": request.method,
                "status_code": response.status_code,
                "extra_data": {"duration_ms": duration_ms},
            }
        )
        return response

    @app.errorhandler(Exception)
    def handle_exception(error):
        request_id = getattr(g, "request_id", "unknown")

        app.logger_json.error(
            "unhandled exception",
            exc_info=True,
            extra={
                "request_id": request_id,
                "path": request.path if request else "unknown",
                "method": request.method if request else "unknown",
            }
        )

        return jsonify({
            "error": "Internal server error",
            "request_id": request_id
        }), 500

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

    @app.route("/login-test")
    def login_test():
        session["user"] = "mikhail"
        return jsonify({"message": "session saved"})

    @app.route("/me")
    def me():
        return jsonify({"user": session.get("user")})

    app.register_blueprint(user_bp)
    return app
