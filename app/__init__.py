import signal
import threading
import time
import uuid

import redis
from flask import Flask, jsonify, g, request, session
from flask_migrate import Migrate
from flask_session import Session
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from config import Config
from app.db.database import db
from app.routes.user_routes import user_bp
from app.logger import setup_logger

session_ext = Session()
migrate = Migrate()

_shutdown_state = {
    "is_shutting_down": False,
    "active_requests": 0,
}
_shutdown_lock = threading.Lock()


def _set_shutting_down(signum, frame):
    with _shutdown_lock:
        _shutdown_state["is_shutting_down"] = True


def is_shutting_down():
    with _shutdown_lock:
        return _shutdown_state["is_shutting_down"]


def increment_active_requests():
    with _shutdown_lock:
        _shutdown_state["active_requests"] += 1


def decrement_active_requests():
    with _shutdown_lock:
        if _shutdown_state["active_requests"] > 0:
            _shutdown_state["active_requests"] -= 1


def get_active_requests():
    with _shutdown_lock:
        return _shutdown_state["active_requests"]


def wait_for_db(app, retries=10, delay=2):
    logger = app.logger_json

    for attempt in range(1, retries + 1):
        try:
            with app.app_context():
                with db.engine.connect() as connection:
                    connection.execute(text("SELECT 1"))

            logger.info(
                "database ready",
                extra={
                    "service_name": app.config["SERVICE_NAME"],
                    "extra_data": {"attempt": attempt},
                },
            )
            return
        except OperationalError:
            logger.error(
                "database not ready",
                extra={
                    "service_name": app.config["SERVICE_NAME"],
                    "extra_data": {"attempt": attempt},
                },
            )
            time.sleep(delay)

    raise RuntimeError("Database is not available after several retries.")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    logger = setup_logger()
    app.logger_json = logger

    app.secret_key = app.config["SECRET_KEY"]
    app.config["SESSION_REDIS"] = redis.from_url(app.config["REDIS_URL"])
    session_ext.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)

    signal.signal(signal.SIGTERM, _set_shutting_down)
    signal.signal(signal.SIGINT, _set_shutting_down)

    with app.app_context():
        from app.models.user import User
        wait_for_db(app)

    @app.before_request
    def before_request():
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        g.start_time = time.time()

        if is_shutting_down():
            app.logger_json.info(
                "request rejected during shutdown",
                extra={
                    "service_name": app.config["SERVICE_NAME"],
                    "request_id": g.request_id,
                    "path": request.path,
                    "method": request.method,
                },
            )
            response = jsonify({
                "error": "Service is shutting down",
                "request_id": g.request_id,
            })
            response.status_code = 503
            response.headers["X-Request-ID"] = g.request_id
            return response

        increment_active_requests()

        app.logger_json.info(
            "request started",
            extra={
                "service_name": app.config["SERVICE_NAME"],
                "request_id": g.request_id,
                "path": request.path,
                "method": request.method,
            },
        )

    @app.after_request
    def after_request(response):
        request_id = getattr(g, "request_id", str(uuid.uuid4()))
        start_time = getattr(g, "start_time", time.time())
        duration_ms = round((time.time() - start_time) * 1000, 2)

        response.headers["X-Request-ID"] = request_id

        app.logger_json.info(
            "request finished",
            extra={
                "service_name": app.config["SERVICE_NAME"],
                "request_id": request_id,
                "path": request.path,
                "method": request.method,
                "status_code": response.status_code,
                "extra_data": {"duration_ms": duration_ms},
            },
        )

        decrement_active_requests()
        return response

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    @app.errorhandler(Exception)
    def handle_exception(error):
        request_id = getattr(g, "request_id", "unknown")

        app.logger_json.error(
            "unhandled exception",
            exc_info=True,
            extra={
                "service_name": app.config["SERVICE_NAME"],
                "request_id": request_id,
                "path": request.path if request else "unknown",
                "method": request.method if request else "unknown",
            },
        )

        return jsonify({
            "error": "Internal server error",
            "request_id": request_id,
        }), 500

    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "message": "API работает",
            "available_routes": [
                "GET /",
                "GET /health",
                "GET /users",
                "POST /users",
                "GET /whoami",
                "GET /login-test",
                "GET /me",
                "GET /slow",
            ],
            "env": app.config["APP_ENV"],
            "version": app.config["APP_VERSION"],
        })

    @app.route("/health", methods=["GET"])
    def health():
        if is_shutting_down():
            return jsonify({
                "status": "shutting_down",
                "active_requests": get_active_requests(),
            }), 503

        return jsonify({
            "status": "ok",
            "active_requests": get_active_requests(),
        })

    @app.route("/login-test", methods=["GET"])
    def login_test():
        session["user"] = "mikhail"
        return jsonify({"message": "session saved"})

    @app.route("/me", methods=["GET"])
    def me():
        return jsonify({"user": session.get("user")})

    @app.route("/slow", methods=["GET"])
    def slow():
        time.sleep(8)
        return jsonify({"status": "done"})

    app.register_blueprint(user_bp)
    return app
