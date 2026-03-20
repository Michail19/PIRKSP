from app.db.database import db
from app.models.user import User


def get_all_users():
    return User.query.all()


def create_user(name: str):
    user = User(name=name)
    db.session.add(user)
    db.session.commit()
    return user
