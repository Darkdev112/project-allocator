from langchain.chat_models import init_chat_model
from config import Config

def get_model():
    model = init_chat_model(
        model="gpt-oss-120b:free",
        model_provider="openai",
        base_url="https://openrouter.ai/api/v1",
        api_key=Config.OPENROUTER_API_KEY,
    )
    return model