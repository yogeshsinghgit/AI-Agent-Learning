from typing import Type
from app.core.config import settings


from app.domains.ai.llms.enums import LLMProvider
from app.domains.ai.providers.groq import GroqProvider
from app.domains.ai.providers.base import BaseLLMProvider
# from .providers.openai import OpenAIProvider
# from .providers.gemini import GeminiProvider


PROVIDERS: dict[LLMProvider,Type[BaseLLMProvider],] = {
            LLMProvider.GROQ: GroqProvider,
            # LLMProvider.OPENAI: OpenAIProvider,
            # LLMProvider.GEMINI: GeminiProvider,
            # LLMProvider.ANTHROPIC: AnthropicProvider,
        }


class LLMFactory:

    @staticmethod
    def get_provider() -> BaseLLMProvider:
        try:
            provider = LLMProvider(settings.LLM_PROVIDER)
        except ValueError as exc:
            raise ValueError(
                f"Invalid LLM Provider: {settings.LLM_PROVIDER}"
            ) from exec

        provider_cls = PROVIDERS.get(provider)

        if provider_cls is None:
            raise ValueError(
                f"Unsupported LLM Provider : {provider}"
            )

        return provider_cls()