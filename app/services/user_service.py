from app.db.database import db
from app.models.user import User

def get_all_users():
    users = User.query.all()
    return [user.to_dict() for user in users]

def add_user(name: str):
    user = User(name=name)
    db.session.add(user)
    db.session.commit()
    return user.to_dict()
