import json
from langchain_community.document_loaders import PyPDFLoader
from config import Config,ResumeResponse,ProjectResponse
from model import get_model
from prompt import prompt,summary_prompt

def get_schema(entity_type):
    ResponseType = ResumeResponse if entity_type == "resume" else ProjectResponse
    schema = {k:v for k,v in ResponseType.model_json_schema().items()}
    schema = {'properties': schema['properties'], 'required': schema['required']}
    return schema

def get_context(doc_path,llm,entity_type):
    file_loader=PyPDFLoader(file_path=doc_path)
    documents=file_loader.load()
    content = documents[0].page_content
    schema = get_schema(entity_type)
    response = llm.invoke(prompt.format(content=content, schema=schema))
    summary_response = llm.invoke(summary_prompt.format(content=content))
    response_json = json.loads(response.content)
    response_json['summary'] = summary_response.content
    return response_json

# get_context('./documents/sample_doc.pdf',get_model(),"resume")