import os
from typing import Any, Dict, List, Optional, Tuple

import requests
import streamlit as st


def _api_base_url() -> str:
    # Allow overriding via env var for deploys.
    return os.getenv("BACKEND_BASE_URL", "http://localhost:8000").rstrip("/")


def _post_pdf(endpoint: str, pdf_bytes: bytes, filename: str) -> Dict[str, Any]:
    url = f"{_api_base_url()}{endpoint}"
    files = {"file": (filename, pdf_bytes, "application/pdf")}
    resp = requests.post(url, files=files, timeout=300)
    resp.raise_for_status()
    return resp.json()


def _get_json(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
    url = f"{_api_base_url()}{endpoint}"
    resp = requests.get(url, params=params, timeout=120)
    resp.raise_for_status()
    return resp.json()


def _safe_error_detail(exc: Exception) -> str:
    if isinstance(exc, requests.HTTPError) and exc.response is not None:
        try:
            data = exc.response.json()
            if isinstance(data, dict) and "detail" in data:
                return str(data["detail"])
        except Exception:
            pass
        return f"HTTP {exc.response.status_code}: {exc.response.text}"
    return str(exc)


def _paginate(items: List[Any], page: int, page_size: int) -> Tuple[List[Any], int]:
    if page_size <= 0:
        return items, 1
    total_pages = max(1, (len(items) + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end], total_pages


def user_page() -> None:
    st.header("User")
    st.caption("Upload your resume PDF to register and then view your dashboard.")

    if "user_registered_id" not in st.session_state:
        st.session_state.user_registered_id = None

    uploaded = st.file_uploader("Upload resume (PDF)", type=["pdf"], key="user_pdf")
    register_col, next_col = st.columns([1, 1])

    with register_col:
        if st.button("Register", type="primary", disabled=uploaded is None):
            try:
                with st.spinner("Registering resume..."):
                    data = _post_pdf(
                        endpoint="/users/register",
                        pdf_bytes=uploaded.getvalue(),
                        filename=uploaded.name,
                    )
                user_id = data.get("user_id")
                if not user_id:
                    st.error("Backend did not return user_id.")
                else:
                    st.session_state.user_registered_id = user_id
                    st.success(f"Registered. Your user id is {user_id}")
            except Exception as e:
                st.error(_safe_error_detail(e))

    with next_col:
        if st.button("Next", disabled=not st.session_state.user_registered_id):
            st.session_state.user_step = "dashboard"

    if st.session_state.get("user_step") == "dashboard" and st.session_state.user_registered_id:
        st.subheader("Dashboard")
        user_id = st.session_state.user_registered_id
        st.write(f"User ID: `{user_id}`")
        try:
            with st.spinner("Loading user details..."):
                user = _get_json(f"/users/{user_id}")
            st.json(user)
        except Exception as e:
            st.error(_safe_error_detail(e))


def admin_page() -> None:
    st.header("Admin")
    st.caption("Upload new jobs, browse existing jobs, and get top-matching users.")

    tab_upload, tab_browse, tab_match = st.tabs(
        ["Enter new job (upload)", "Browse jobs", "Match users for a job"]
    )

    with tab_upload:
        st.subheader("Upload job description (PDF)")
        job_pdf = st.file_uploader("Upload job PDF", type=["pdf"], key="admin_job_pdf")
        if st.button("Upload job", type="primary", disabled=job_pdf is None):
            try:
                with st.spinner("Uploading and processing job..."):
                    data = _post_pdf(
                        endpoint="/admin/upload-project",
                        pdf_bytes=job_pdf.getvalue(),
                        filename=job_pdf.name,
                    )
                project_id = data.get("project_id")
                if not project_id:
                    st.error("Backend did not return project_id.")
                else:
                    st.success(f"Uploaded. Project ID: {project_id}")
            except Exception as e:
                st.error(_safe_error_detail(e))

    with tab_browse:
        st.subheader("All projects (paginated)")
        page_size = st.selectbox("Page size", [5, 10, 20, 50], index=1, key="projects_page_size")
        page = st.number_input("Page", min_value=1, value=1, step=1, key="projects_page")

        if st.button("Refresh projects"):
            st.session_state.pop("all_projects_cache", None)

        try:
            if "all_projects_cache" not in st.session_state:
                with st.spinner("Loading projects..."):
                    payload = _get_json("/admin/get_all_projects")
                st.session_state.all_projects_cache = payload.get("projects", [])

            projects = st.session_state.all_projects_cache
            page_items, total_pages = _paginate(projects, int(page), int(page_size))
            st.caption(f"Total projects: {len(projects)} | Pages: {total_pages}")

            if not projects:
                st.info("No projects found in the database yet.")
            else:
                options = {
                    p["project_id"]: p
                    for p in page_items
                    if isinstance(p, dict) and "project_id" in p
                }
                if not options:
                    st.warning("No valid projects on this page.")
                else:
                    selected_id = st.selectbox(
                        "Select a project on this page",
                        list(options.keys()),
                        key="browse_selected_project",
                    )
                    st.subheader("Project details")
                    st.json(options[selected_id])
        except Exception as e:
            st.error(_safe_error_detail(e))

    with tab_match:
        st.subheader("Get top suitable users for a project")
        top_k = st.slider("top_k", min_value=1, max_value=20, value=5, step=1)

        try:
            with st.spinner("Loading projects..."):
                payload = _get_json("/admin/get_all_projects")
            projects = payload.get("projects", [])
            project_ids = [
                p.get("project_id")
                for p in projects
                if isinstance(p, dict) and p.get("project_id")
            ]
            if not project_ids:
                st.info("No projects available. Upload a job first.")
            else:
                selected_project_id = st.selectbox("Project", project_ids, key="match_project_id")
                if st.button("Find suitable users", type="primary"):
                    with st.spinner("Matching users..."):
                        result = _get_json(
                            f"/admin/projects/{selected_project_id}/users",
                            params={"top_k": int(top_k)},
                        )
                    users = result.get("users", [])
                    st.caption(f"Matched users: {len(users)}")
                    for idx, u in enumerate(users, start=1):
                        user_id = u.get("user_id")
                        profile = u.get("user_profile")
                        with st.expander(f"{idx}. {user_id}", expanded=(idx == 1)):
                            st.json(profile if profile is not None else u)
        except Exception as e:
            st.error(_safe_error_detail(e))


def main() -> None:
    st.set_page_config(page_title="Project Allocator", layout="wide")
    st.title("Project Allocator")

    with st.sidebar:
        st.subheader("Navigation")
        page = st.radio("Go to", ["User", "Admin"], index=0)
        st.divider()
        st.subheader("Backend")
        st.code(_api_base_url(), language="text")
        st.caption("Set BACKEND_BASE_URL to point to your FastAPI server.")

    if page == "User":
        user_page()
    else:
        admin_page()


if __name__ == "__main__":
    main()

