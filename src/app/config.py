import os
from dotenv import load_dotenv
from typing import Literal
from pydantic import BaseModel
load_dotenv()

class Config:
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class ResumeResponse(BaseModel):
    entity_type:Literal["user"]
    role:str
    seniority:str
    total_experience_years:int
    primary_skills:list[str]
    secondary_skills:list[str]
    domains:list[str]
    summary:str

class ProjectResponse(BaseModel):
    entity_type:Literal["project"]
    required_role:str
    required_seniority:str
    required_experience_years:int
    required_skills:list[str]
    optional_skills:list[str]
    required_domains:list[str]
    summary:str