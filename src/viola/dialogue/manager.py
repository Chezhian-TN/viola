from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage

from viola.agent.viola_agent import ViolaAgent
from viola.config import Settings
from viola.memory.context import ConversationSession


@dataclass(frozen=True)
class AssistantReply:
    content: str
    thread_id: str


class DialogueManager:
    """Coordinates user turns, agent execution, and response rendering."""

    def __init__(self, settings: Settings) -> None:
        self.agent = ViolaAgent(settings)

    def new_session(
        self,
        *,
        user_id: str = "local-user",
        thread_id: str | None = None,
    ) -> ConversationSession:
        return self.agent.context_manager.new_session(user_id=user_id, thread_id=thread_id)

    def ask(self, user_message: str, session: ConversationSession) -> AssistantReply:
        result = self.agent.invoke(user_message, session)
        return AssistantReply(
            content=self._extract_response_text(result),
            thread_id=session.thread_id,
        )

    def _extract_response_text(self, result: dict[str, Any]) -> str:
        messages = result.get("messages", [])
        for message in reversed(messages):
            if isinstance(message, AIMessage):
                return self._content_to_text(message.content)
            if isinstance(message, dict) and message.get("role") == "assistant":
                return self._content_to_text(message.get("content", ""))
        return "I completed the turn, but no assistant message was returned."

    def _content_to_text(self, content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for block in content:
                if isinstance(block, str):
                    parts.append(block)
                elif isinstance(block, dict):
                    text = block.get("text") or block.get("content")
                    if text:
                        parts.append(str(text))
                elif isinstance(block, BaseMessage):
                    parts.append(self._content_to_text(block.content))
            if parts:
                return "\n".join(parts)
        return json.dumps(content, ensure_ascii=False, indent=2)

