from vector_db import create_store
from langchain_core.documents import Document
from uuid import uuid4
import json

vector_db = create_store()

dict1 = {
    "entity_type": "user",
    "role": "Data Engineer",
    "seniority": "senior",
    "total_experience_years": 6,
    "primary_skills": ["Python", "Spark", "Kafka", "Airflow"],
    "secondary_skills": ["AWS", "Snowflake", "Terraform"],
    "domains": ["FinTech", "Data Platforms"],
    "summary": "Senior data engineer with 6 years of experience designing and maintaining large-scale data pipelines and streaming systems using Spark, Kafka, and Airflow in cloud environments."
}

dict2 = {
    "entity_type": "user",
    "role": "Machine Learning Engineer",
    "seniority": "mid",
    "total_experience_years": 4,
    "primary_skills": ["Python", "TensorFlow", "PyTorch", "Scikit-learn"],
    "secondary_skills": ["Docker", "Kubernetes", "AWS"],
    "domains": ["Healthcare", "AI Platforms"],
    "summary": "Machine learning engineer with 4 years of experience building, training, and deploying production-grade ML models and APIs using Python, TensorFlow, and PyTorch."
}

dict3 = {
    "entity_type": "user",
    "role": "Backend Engineer",
    "seniority": "junior",
    "total_experience_years": 1,
    "primary_skills": ["Node.js", "Express", "MongoDB"],
    "secondary_skills": ["Docker", "GitHub Actions"],
    "domains": ["E-commerce", "APIs"],
    "summary": "Junior backend engineer with 1 year of experience developing RESTful APIs and microservices using Node.js, Express, and MongoDB, with exposure to CI/CD and containerized deployments."
}

document_1 = Document(
    page_content=json.dumps(dict1)
)

document_2 = Document(
    page_content=json.dumps(dict2)
)

document_3 = Document(
    page_content=json.dumps(dict3)
)


documents = [
    document_1,
    document_2,
    document_3,
]

uuids = ['user1','user2','user3']
vector_db.add_documents(documents=documents, ids=uuids)

project_1 = {
    "entity_type": "project",
    "required_role": "Backend Engineer",
    "required_seniority": "mid",
    "required_experience_years": 2,
    "required_skills": ["Python", "Django", "PostgreSQL", "Kafka"],
    "optional_skills": ["Docker", "AWS"],
    "required_domains": ["FinTech", "Payments"],
    "summary": "Build and maintain high-throughput backend services for a FinTech payments platform using Python, Django, Kafka, and PostgreSQL."
  }

document_4 = Document(
    page_content=json.dumps(project_1)
)
vector_db.add_documents(documents=[document_4], ids=["project_1"])

results = vector_db.similarity_search("Give me top 2 resumes for project_1", k=2)
for result in results:
    print(result.page_content)
    print("\n")