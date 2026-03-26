import argparse

import redis as redis_lib
from flask_migrate import upgrade
from gunicorn.app.wsgiapp import WSGIApplication

from app import create_app
from app.db.database import db
from app.models.user import User


def run_server():
    WSGIApplication("%(prog)s [OPTIONS] [APP_MODULE]").run()


def run_migrations(app):
    with app.app_context():
        upgrade()
        app.logger_json.info(
            "migrations applied successfully",
            extra={"service_name": app.config["SERVICE_NAME"]},
        )


def create_admin(app, email, name):
    with app.app_context():
        existing = User.query.filter_by(email=email).first()
        if existing:
            app.logger_json.info(
                "admin already exists",
                extra={
                    "service_name": app.config["SERVICE_NAME"],
                    "extra_data": {"email": email},
                },
            )
            return

        user = User(name=name, email=email, is_admin=True)
        db.session.add(user)
        db.session.commit()

        app.logger_json.info(
            "admin created",
            extra={
                "service_name": app.config["SERVICE_NAME"],
                "extra_data": {"email": email},
            },
        )


def clear_cache(app):
    redis_client = redis_lib.from_url(app.config["REDIS_URL"])
    redis_client.flushdb()

    app.logger_json.info(
        "redis cache cleared",
        extra={"service_name": app.config["SERVICE_NAME"]},
    )


def main():
    parser = argparse.ArgumentParser(description="PIRKSP administrative CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    server_parser = subparsers.add_parser("server")
    server_parser.add_argument("--bind", default="0.0.0.0:5000")
    server_parser.add_argument("--workers", default="2")
    server_parser.add_argument("--graceful-timeout", default="10")
    server_parser.add_argument("--timeout", default="30")

    subparsers.add_parser("migrate")

    create_admin_parser = subparsers.add_parser("create-admin")
    create_admin_parser.add_argument("--email", required=True)
    create_admin_parser.add_argument("--name", required=True)

    subparsers.add_parser("clear-cache")

    args, unknown = parser.parse_known_args()
    app = create_app()

    if args.command == "server":
        import sys
        sys.argv = [
            "gunicorn",
            "--bind", args.bind,
            "--workers", args.workers,
            "--graceful-timeout", args.graceful_timeout,
            "--timeout", args.timeout,
            "wsgi:app",
        ] + unknown
        run_server()
    elif args.command == "migrate":
        run_migrations(app)
    elif args.command == "create-admin":
        create_admin(app, args.email.strip().lower(), args.name.strip())
    elif args.command == "clear-cache":
        clear_cache(app)


if __name__ == "__main__":
    main()
