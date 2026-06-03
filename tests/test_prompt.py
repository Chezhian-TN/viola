from pathlib import Path

from viola.config import Settings
from viola.prompts.system import build_system_prompt


def test_system_prompt_includes_assistant_name_and_timezone() -> None:
    settings = Settings(
        assistant_name="Viola",
        model="openai:test",
        temperature=0.3,
        max_retries=6,
        request_timeout=60,
        default_timezone="Asia/Calcutta",
        data_dir=Path(".viola_data"),
        tavily_max_results=5,
        langsmith_tracing=False,
    )

    prompt = build_system_prompt(settings)

    assert "You are Viola" in prompt
    assert "Asia/Calcutta" in prompt
    assert "Use web search" in prompt

