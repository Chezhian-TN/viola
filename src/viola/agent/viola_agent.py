from __future__ import annotations

import os
from typing import Any

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from viola.config import Settings
from viola.memory.context import ContextManager, ConversationSession
from viola.prompts.system import build_system_prompt
from viola.tools.registry import build_tools

PROVIDER_KEY_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    "google_genai": "GOOGLE_API_KEY",
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}


class ViolaAgent:
    """Builds and invokes the LangChain agent graph for Viola."""

    def __init__(
        self,
        settings: Settings,
        *,
        context_manager: ContextManager | None = None,
    ) -> None:
        self.settings = settings
        self.context_manager = context_manager or ContextManager()
        self.tools = build_tools(settings)
        self.model = self._build_model()
        self.agent = create_agent(
            model=self.model,
            tools=self.tools,
            system_prompt=build_system_prompt(settings),
            checkpointer=self.context_manager.checkpointer,
            name="viola",
        )

    def invoke(self, user_message: str, session: ConversationSession) -> dict[str, Any]:
        return self.agent.invoke(
            {"messages": [{"role": "user", "content": user_message}]},
            config=self.context_manager.config_for(session),
        )

    def _build_model(self) -> Any:
        self._validate_provider_credentials()
        return init_chat_model(
            self.settings.model,
            temperature=self.settings.temperature,
            max_retries=self.settings.max_retries,
            timeout=self.settings.request_timeout,
        )

    def _validate_provider_credentials(self) -> None:
        provider = self.settings.model.split(":", maxsplit=1)[0]
        key_name = PROVIDER_KEY_ENV.get(provider)
        if key_name and not os.getenv(key_name):
            raise RuntimeError(
                f"{key_name} is required for model {self.settings.model!r}. "
                "Set it in your environment or .env file."
            )

