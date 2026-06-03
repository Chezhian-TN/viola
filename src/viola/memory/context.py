from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver


@dataclass(frozen=True)
class ConversationSession:
    """Identifies a user conversation so LangChain can restore message history."""

    user_id: str = "local-user"
    thread_id: str = field(default_factory=lambda: str(uuid4()))


class ContextManager:
    """Owns short-term conversational memory for local sessions."""

    def __init__(self, checkpointer: InMemorySaver | None = None) -> None:
        self.checkpointer = checkpointer or InMemorySaver()

    def new_session(
        self,
        *,
        user_id: str = "local-user",
        thread_id: str | None = None,
    ) -> ConversationSession:
        return ConversationSession(user_id=user_id, thread_id=thread_id or str(uuid4()))

    def config_for(self, session: ConversationSession) -> RunnableConfig:
        return {
            "configurable": {"thread_id": session.thread_id},
            "metadata": {"user_id": session.user_id},
        }

