from vector_db import create_store
from model import get_model
from utilities import get_context

from user_db import insert_user, get_all_users
from project_db import insert_project


vector_db = create_store()
llm = get_model()


def register_user(resume_path: str):
    """
    Parse resume → persist user → store embedding
    """
    # Parse resume
    user_data = get_context(
        doc_path=resume_path,
        llm=llm,
        entity_type="resume"
    )

    # Persist user (file-backed)
    user_id = insert_user(user_data)

    # Store embedding in Pinecone
    vector_db.add_texts(
        texts=[user_data["summary"]],
        metadatas=[{
            "entity_type": "user",
            "user_id": user_id
        }],
        ids=[user_id]
    )

    return {
        "status": "success",
        "user_id": user_id
    }


def register_project(project_doc_path: str):
    """
    Parse project → persist project → store embedding
    """
    project_data = get_context(
        doc_path=project_doc_path,
        llm=llm,
        entity_type="project"
    )

    # Persist project (file-backed)
    project_id = insert_project(project_data)

    # Store embedding in Pinecone
    vector_db.add_texts(
        texts=[project_data["summary"]],
        metadatas=[{
            "entity_type": "project",
            "project_id": project_id
        }],
        ids=[project_id]
    )

    return {
        "status": "success",
        "project_id": project_id
    }


def get_users(project_summary: str, top_k: int = 5):
    """
    Given a project summary, return best matching users
    """
    # Vector similarity search
    results = vector_db.similarity_search(
        query=project_summary,
        k=top_k,
        filter={"entity_type": "user"}
    )

    # Load persisted users from file
    users = get_all_users()
    user_lookup = {u["user_id"]: u for u in users}

    matched_users = []
    for doc in results:
        user_id = doc.metadata.get("user_id")
        if user_id and user_id in user_lookup:
            matched_users.append({
                "user_id": user_id,
                "user_profile": user_lookup[user_id]
            })

    return matched_users
