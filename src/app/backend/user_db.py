
import json
import uuid
from typing import List, Dict, Any, Optional

from dbconnect import get_connection


def _serialize_list(value: Any) -> str:
    """
    Store list fields as JSON text in the database.
    """
    if value is None:
        return json.dumps([])
    if isinstance(value, list):
        return json.dumps(value)
    return json.dumps([value])


def _deserialize_list(text: Optional[str]) -> List[Any]:
    if not text:
        return []
    try:
        data = json.loads(text)
        return data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        return []


def insert_user(user_data: Dict[str, Any]) -> str:
    """
    Insert a new user into the SQL database.
    """
    user_id = f"user_{uuid.uuid4()}"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users (
            user_id,
            entity_type,
            role,
            seniority,
            total_experience_years,
            primary_skills,
            secondary_skills,
            domains,
            summary,
            file_link
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            user_id,
            user_data.get("entity_type"),
            user_data.get("role"),
            user_data.get("seniority"),
            user_data.get("total_experience_years"),
            _serialize_list(user_data.get("primary_skills")),
            _serialize_list(user_data.get("secondary_skills")),
            _serialize_list(user_data.get("domains")),
            user_data.get("summary"),
            None,  # file_link placeholder for future use
        ),
    )

    conn.commit()
    cursor.close()
    conn.close()

    return user_id


def _row_to_user(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a DB row into the user dict format expected by the rest of the app.
    """
    row["primary_skills"] = _deserialize_list(row.get("primary_skills"))
    row["secondary_skills"] = _deserialize_list(row.get("secondary_skills"))
    row["domains"] = _deserialize_list(row.get("domains"))
    return row


def get_all_users() -> List[Dict[str, Any]]:
    """
    Read all users from the SQL database.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT
            user_id,
            entity_type,
            role,
            seniority,
            total_experience_years,
            primary_skills,
            secondary_skills,
            domains,
            summary,
            file_link
        FROM users
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [_row_to_user(row) for row in rows]


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a single user by ID from the SQL database.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT
            user_id,
            entity_type,
            role,
            seniority,
            total_experience_years,
            primary_skills,
            secondary_skills,
            domains,
            summary,
            file_link
        FROM users
        WHERE user_id = %s
        """,
        (user_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return None

    return _row_to_user(row)


def delete_user(user_id: str) -> bool:
    """
    Delete a user by ID from the SQL database.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    return affected > 0
