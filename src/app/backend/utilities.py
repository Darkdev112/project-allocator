import json
import random
import time
from langchain_community.document_loaders import PyPDFLoader
from .config import Config, ResumeResponse, ProjectResponse
from .model import get_model
from .prompt import prompt, summary_prompt

def get_schema(entity_type):
    ResponseType = ResumeResponse if entity_type == "resume" else ProjectResponse
    schema = {k:v for k,v in ResponseType.model_json_schema().items()}
    schema = {'properties': schema['properties'], 'required': schema['required']}
    return schema

def _invoke_with_retry(llm, prompt_text: str, *, attempts: int = 5, base_delay_s: float = 1.0):
    last_exc: Exception | None = None
    for i in range(attempts):
        try:
            return llm.invoke(prompt_text)
        except Exception as e:
            last_exc = e
            msg = str(e).lower()
            is_rate_limited = ("429" in msg) or ("rate limit" in msg) or ("rate-limited" in msg)
            if not is_rate_limited or i == attempts - 1:
                raise
            # Exponential backoff with jitter.
            delay = base_delay_s * (2 ** i) + random.uniform(0.0, 0.25)
            time.sleep(delay)
    if last_exc:
        raise last_exc

def get_context(doc_path,llm,entity_type):
    file_loader=PyPDFLoader(file_path=doc_path)
    documents=file_loader.load()
    content = documents[0].page_content
    schema = get_schema(entity_type)
    response = _invoke_with_retry(llm, prompt.format(content=content, schema=schema))
    summary_response = _invoke_with_retry(llm, summary_prompt.format(content=content))
    response_json = json.loads(response.content)
    response_json['summary'] = summary_response.content
    return response_json

# get_context('./documents/sample_doc.pdf',get_model(),"resume")