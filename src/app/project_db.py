# project_db.py

import json
import uuid
import os
from typing import List, Dict

PROJECTS_FILE = "projects.json"


def _load_projects() -> List[Dict]:
    if not os.path.exists(PROJECTS_FILE):
        return []
    with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_projects(projects: List[Dict]):
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2)


def insert_project(project_data: Dict) -> str:
    projects = _load_projects()

    project_id = f'project_{str(uuid.uuid4())}'
    record = {
        "project_id": project_id,
        **project_data
    }

    projects.append(record)
    _save_projects(projects)

    return project_id


def get_all_projects() -> List[Dict]:
    """
    Read all projects from projects.json
    """
    return _load_projects()


def get_project_by_id(project_id: str) -> Dict | None:
    """
    Fetch a single project by ID
    """
    projects = _load_projects()
    return next((p for p in projects if p["project_id"] == project_id), None)


def delete_project(project_id: str) -> bool:
    """
    Delete project by ID
    """
    projects = _load_projects()
    new_projects = [p for p in projects if p["project_id"] != project_id]

    if len(projects) == len(new_projects):
        return False

    _save_projects(new_projects)
    return True
