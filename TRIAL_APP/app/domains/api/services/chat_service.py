from typing import Any
from langchain_core.messages import HumanMessage
from loguru import logger


class ChatService:
    """
    Service to handle chat interaction with the AI Agent graph.
    """

    def __init__(self, graph: Any) -> None:
        self._graph = graph

    async def send_message(self, message: str, thread_id: str) -> str:
        """
        Sends a user message to the compiled agent graph, scoped by thread ID,
        and returns the final agent's response content.
        """
        logger.info(
            "ChatService: Sending message to agent on thread '{}': '{}'",
            thread_id,
            message,
        )

        config = {"configurable": {"thread_id": thread_id}}
        inputs = {"messages": [HumanMessage(content=message)]}

        try:
            result = await self._graph.ainvoke(inputs, config=config)

            messages = result.get("messages", [])
            if not messages:
                logger.warning("ChatService: Received empty message sequence from agent graph.")
                return "No response from travel agent."

            # Retrieve the last AI message in the chat history
            final_message = messages[-1]
            logger.success(
                "ChatService: Received response from agent graph: '{}'",
                final_message.content,
            )
            return final_message.content

        except Exception as exc:
            logger.error("ChatService: Error invoking agent graph.")
            raise exc
