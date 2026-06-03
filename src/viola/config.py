from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be a float, got {value!r}") from exc


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer, got {value!r}") from exc


@dataclass(frozen=True)
class Settings:
    assistant_name: str
    model: str
    temperature: float
    max_retries: int
    request_timeout: int
    default_timezone: str
    data_dir: Path
    tavily_max_results: int
    langsmith_tracing: bool


def load_settings(
    env_file: str | Path | None = None,
    *,
    load_dotenv_file: bool = True,
) -> Settings:
    """Load application settings from environment variables and an optional .env file."""
    if load_dotenv_file:
        if env_file is None:
            load_dotenv()
        else:
            load_dotenv(dotenv_path=env_file)

    return Settings(
        assistant_name=os.getenv("VIOLA_ASSISTANT_NAME", "Viola"),
        model=os.getenv("VIOLA_MODEL", "openai:gpt-4.1-mini"),
        temperature=_float_env("VIOLA_TEMPERATURE", 0.3),
        max_retries=_int_env("VIOLA_MAX_RETRIES", 6),
        request_timeout=_int_env("VIOLA_REQUEST_TIMEOUT", 60),
        default_timezone=os.getenv("VIOLA_DEFAULT_TIMEZONE", "Asia/Calcutta"),
        data_dir=Path(os.getenv("VIOLA_DATA_DIR", ".viola_data")).expanduser(),
        tavily_max_results=_int_env("VIOLA_TAVILY_MAX_RESULTS", 5),
        langsmith_tracing=_bool_env("LANGSMITH_TRACING", False),
    )

