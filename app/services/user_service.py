from flask import current_app, g

from app.repositories.user_repository import (
    get_all_users as repo_get_all_users,
    create_user as repo_create_user,
    create_admin_user as repo_create_admin_user,
)


def get_all_users():
    current_app.logger_json.info(
        "fetch all users",
        extra={
            "service_name": current_app.config["SERVICE_NAME"],
            "request_id": getattr(g, "request_id", "unknown"),
        },
    )

    users = repo_get_all_users()
    return [user.to_dict() for user in users]


def add_user(name: str):
    cleaned_name = name.strip()

    current_app.logger_json.info(
        "create user",
        extra={
            "service_name": current_app.config["SERVICE_NAME"],
            "request_id": getattr(g, "request_id", "unknown"),
            "extra_data": {"name": cleaned_name},
        },
    )

    user = repo_create_user(cleaned_name)
    return user.to_dict()


def create_admin(name: str, email: str):
    user, created = repo_create_admin_user(name=name.strip(), email=email.strip().lower())

    current_app.logger_json.info(
        "create admin user",
        extra={
            "service_name": current_app.config["SERVICE_NAME"],
            "request_id": getattr(g, "request_id", "unknown"),
            "extra_data": {
                "email": user.email,
                "created": created,
            },
        },
    )

    return user.to_dict(), created
