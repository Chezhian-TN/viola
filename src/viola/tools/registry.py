from __future__ import annotations

from langchain_core.tools import BaseTool

from viola.config import Settings
from viola.tools.tasks import build_task_tools
from viola.tools.time import build_time_tools
from viola.tools.web_search import build_web_search_tool


def build_tools(settings: Settings) -> list[BaseTool]:
    return [
        build_web_search_tool(settings),
        *build_task_tools(settings.data_dir),
        *build_time_tools(settings.default_timezone),
    ]

