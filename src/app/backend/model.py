import os

from langchain.chat_models import init_chat_model
from .config import Config

def get_model():
    model_name = os.getenv("OPENROUTER_MODEL", "openai/gpt-oss-20b:free")
    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    model = init_chat_model(
        model=model_name,
        # OpenRouter is OpenAI-compatible; keeping the provider as "openai"
        # avoids requiring provider-specific LangChain packages (e.g. langchain-mistralai).
        model_provider="openai",
        base_url=base_url,
        api_key=Config.OPENROUTER_API_KEY,
    )
    return model