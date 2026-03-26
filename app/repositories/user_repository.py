from app.db.database import db
from app.models.user import User


def get_all_users():
    return User.query.order_by(User.id.asc()).all()


def create_user(name: str, email: str | None = None, is_admin: bool = False):
    user = User(name=name, email=email, is_admin=is_admin)
    db.session.add(user)
    db.session.commit()
    return user


def get_user_by_email(email: str):
    return User.query.filter_by(email=email).first()


def create_admin_user(name: str, email: str):
    existing = get_user_by_email(email)
    if existing:
        return existing, False

    user = User(name=name, email=email, is_admin=True)
    db.session.add(user)
    db.session.commit()
    return user, True
