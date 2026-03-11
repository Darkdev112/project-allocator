import os
import tempfile
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel

from controller import register_user, register_project, get_users
from user_db import get_all_users, get_user_by_id
from project_db import get_project_by_id, get_all_projects


app = FastAPI(title="Project Allocator API")


def _save_uploaded_file(uploaded_file: UploadFile) -> str:
    """
    Persist an uploaded file to a temporary location and return the path.
    """
    suffix = os.path.splitext(uploaded_file.filename or "")[1] or ".pdf"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded_file.file.read())
    tmp.close()
    return tmp.name


class UserIdsRequest(BaseModel):
    user_ids: List[str]


@app.post("/users/register")
async def register_user_endpoint(file: UploadFile = File(...)):
    """
    Endpoint for users to upload their resume (PDF).
    """
    if file.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    tmp_path = _save_uploaded_file(file)
    try:
        result = register_user(tmp_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.get("/users/{user_id}")
def get_user_by_id_endpoint(user_id: str):
    """
    Fetch a user's details from the SQL database by user_id.
    """
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{user_id}' not found.")
    return user


@app.post("/admin/upload-project")
async def upload_project_endpoint(file: UploadFile = File(...)):
    """
    Endpoint for admin to upload a project / role PDF.
    Parses the PDF, stores the project in the SQL database, and returns the project ID.
    """
    if file.content_type not in {"application/pdf", "application/x-pdf"}:
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    tmp_path = _save_uploaded_file(file)
    try:
        result = register_project(tmp_path)
        return {
            "project_id": result["project_id"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.get("/admin/get_all_projects")
def get_all_projects_endpoint():
    """
    Endpoint for admin to fetch the list of all projects from the SQL database.
    """
    projects = get_all_projects()
    return {
        "count": len(projects),
        "projects": projects,
    }


@app.get("/admin/projects/{project_id}/users")
def get_project_users_endpoint(project_id: str, top_k: int = 5):
    """
    Return all matched users for a selected project by project ID.
    """
    project = get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found.")

    summary = project.get("summary")
    if not summary:
        raise HTTPException(
            status_code=500,
            detail="Project has no summary; cannot match users.",
        )

    matched_users = get_users(summary, top_k=top_k)
    return {
        "project_id": project_id,
        "count": len(matched_users),
        "users": [
            {"user_id": m["user_id"], "user_profile": m["user_profile"]}
            for m in matched_users
        ],
    }


@app.post("/admin/users/details")
def get_user_details_endpoint(payload: UserIdsRequest):
    """
    Endpoint for admin to fetch full details for a list of users
    from the local DB.
    """
    all_users = get_all_users()
    requested_ids = set(payload.user_ids)
    users_by_id = {u["user_id"]: u for u in all_users}

    found_users = [
        users_by_id[uid] for uid in requested_ids if uid in users_by_id
    ]

    return {
        "count": len(found_users),
        "users": found_users,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
