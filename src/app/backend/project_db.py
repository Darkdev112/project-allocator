import json
import uuid
from typing import List, Dict, Any, Optional

from .dbconnect import get_connection


def _serialize_list(value: Any) -> str:
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


def insert_project(project_data: Dict[str, Any]) -> str:
    """
    Insert a new project into the SQL database.
    """
    project_id = f"project_{uuid.uuid4()}"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO projects (
            project_id,
            entity_type,
            required_role,
            required_seniority,
            required_experience_years,
            required_skills,
            optional_skills,
            required_domains,
            summary,
            file_link
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            project_id,
            project_data.get("entity_type"),
            project_data.get("required_role"),
            project_data.get("required_seniority"),
            project_data.get("required_experience_years"),
            _serialize_list(project_data.get("required_skills")),
            _serialize_list(project_data.get("optional_skills")),
            _serialize_list(project_data.get("required_domains")),
            project_data.get("summary"),
            None,  # file_link placeholder
        ),
    )

    conn.commit()
    cursor.close()
    conn.close()

    return project_id


def _row_to_project(row: Dict[str, Any]) -> Dict[str, Any]:
    row["required_skills"] = _deserialize_list(row.get("required_skills"))
    row["optional_skills"] = _deserialize_list(row.get("optional_skills"))
    row["required_domains"] = _deserialize_list(row.get("required_domains"))
    return row


def get_all_projects() -> List[Dict[str, Any]]:
    """
    Read all projects from the SQL database.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT
            project_id,
            entity_type,
            required_role,
            required_seniority,
            required_experience_years,
            required_skills,
            optional_skills,
            required_domains,
            summary,
            file_link
        FROM projects
        """
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return [_row_to_project(row) for row in rows]


def get_project_by_id(project_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a single project by ID from the SQL database.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT
            project_id,
            entity_type,
            required_role,
            required_seniority,
            required_experience_years,
            required_skills,
            optional_skills,
            required_domains,
            summary,
            file_link
        FROM projects
        WHERE project_id = %s
        """,
        (project_id,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return None

    return _row_to_project(row)


def delete_project(project_id: str) -> bool:
    """
    Delete a project by ID from the SQL database.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM projects WHERE project_id = %s", (project_id,))
    affected = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    return affected > 0
