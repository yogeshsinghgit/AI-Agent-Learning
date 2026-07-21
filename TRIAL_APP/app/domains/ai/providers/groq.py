from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import settings

from .base import BaseLLMProvider


class GroqProvider(BaseLLMProvider):

    def create_model(
        self,
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,) -> BaseChatModel:

        return ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=settings.DEFAULT_MODEL if model is None else model,
            temperature=(
                settings.TEMPERATURE
                if temperature is None
                else temperature
            ),
            max_tokens=(
                settings.MAX_TOKENS
                if max_tokens is None
                else max_tokens
            ),
        )