
import json
import uuid
import os
from typing import List, Dict

USERS_FILE = "users.json"


def _load_users() -> List[Dict]:
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_users(users: List[Dict]):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def insert_user(user_data: Dict) -> str:
    users = _load_users()

    user_id = f'user_{str(uuid.uuid4())}'
    record = {
        "user_id": user_id,
        **user_data
    }

    users.append(record)
    _save_users(users)

    return user_id


def get_all_users() -> List[Dict]:
    """
    Read all users from users.json
    """
    return _load_users()


def get_user_by_id(user_id: str) -> Dict | None:
    """
    Fetch a single user by ID
    """
    users = _load_users()
    return next((u for u in users if u["user_id"] == user_id), None)


def delete_user(user_id: str) -> bool:
    """
    Delete a user by ID
    """
    users = _load_users()
    new_users = [u for u in users if u["user_id"] != user_id]

    if len(users) == len(new_users):
        return False

    _save_users(new_users)
    return True
