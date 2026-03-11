import os
from langchain.chat_models import init_chat_model
from .config import Config


def get_model():
    model_name = os.getenv(
        "OPENROUTER_MODEL",
        "openrouter/free"   # guaranteed free routing
    )

    base_url = os.getenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1"
    )

    model = init_chat_model(
        model=model_name,
        model_provider="openai",   # OpenRouter is OpenAI compatible
        base_url=base_url,
        api_key=Config.OPENROUTER_API_KEY,
        default_headers={
            "HTTP-Referer": "http://localhost",
            "X-Title": "LangChain App"
        }
    )

    return model