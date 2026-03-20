from flask import current_app, g

from app.repositories.user_repository import (
    get_all_users as repo_get_all_users,
    create_user as repo_create_user,
)


def get_all_users():
    current_app.logger_json.info(
        "fetch all users",
        extra={"request_id": getattr(g, "request_id", "unknown")}
    )

    users = repo_get_all_users()
    return [user.to_dict() for user in users]


def add_user(name: str):
    cleaned_name = name.strip()

    current_app.logger_json.info(
        "create user",
        extra={
            "request_id": getattr(g, "request_id", "unknown"),
            "extra_data": {"name": cleaned_name}
        }
    )

    user = repo_create_user(cleaned_name)
    return user.to_dict()
