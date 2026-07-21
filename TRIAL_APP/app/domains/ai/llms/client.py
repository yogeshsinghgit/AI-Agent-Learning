from loguru import logger

from langchain_core.language_models.chat_models import BaseChatModel

from .factory import LLMFactory


class LLMClient:

    def __init__(self):

        self._client: BaseChatModel | None = None

    async def connect(self):

        if self._client is not None:
            return

        logger.info("Initializing LLM")

        provider = LLMFactory.get_provider()

        self._client = provider.create_model()

        logger.success("LLM initialized")

    async def disconnect(self):

        logger.info("Closing LLM")

        self._client = None

    @property
    def client(self) -> BaseChatModel:

        if self._client is None:
            raise RuntimeError("LLM not initialized")

        return self._client