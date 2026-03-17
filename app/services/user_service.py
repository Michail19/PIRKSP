from app.db.database import db

def get_users():
    return db["users"]

def create_user(data):
    user = {
        "id": len(db["users"]) + 1,
        "name": data.get("name")
    }
    db["users"].append(user)
    return user
