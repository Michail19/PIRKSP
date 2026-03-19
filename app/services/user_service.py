from app.db.database import db

def get_all_users():
    return db["users"]

def add_user(name: str):
    users = db["users"]
    new_user = {
        "id": len(users) + 1,
        "name": name
    }
    users.append(new_user)
    return new_user
