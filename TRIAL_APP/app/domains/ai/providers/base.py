from abc import ABC, abstractmethod

from langchain_core.language_models.chat_models import BaseChatModel


class BaseLLMProvider(ABC):

    @abstractmethod
    def create_model(
        self,
        *,
        model: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> BaseChatModel:
        """
        Create and return a LangChain chat model.
        """
        raise NotImplementedError