from __future__ import annotations

import os
from typing import Any

from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field

from viola.config import Settings


class WebSearchInput(BaseModel):
    query: str = Field(description="Search query for current or external information.")


def build_web_search_tool(settings: Settings) -> BaseTool:
    if os.getenv("TAVILY_API_KEY"):
        try:
            from langchain_tavily import TavilySearch
        except ImportError:
            return _build_unavailable_search_tool(
                "TAVILY_API_KEY is set, but langchain-tavily is not installed."
            )

        return TavilySearch(
            max_results=settings.tavily_max_results,
            include_answer=True,
            search_depth="basic",
        )

    return _build_duckduckgo_search_tool(max_results=settings.tavily_max_results)


def _build_duckduckgo_search_tool(max_results: int) -> BaseTool:
    @tool("web_search", args_schema=WebSearchInput)
    def web_search(query: str) -> str:
        """Search the public web and return concise result snippets."""
        try:
            DDGS = _load_ddgs()
        except ImportError:
            return (
                "Web search is unavailable. Install ddgs or set TAVILY_API_KEY "
                "to use Tavily search."
            )

        try:
            with DDGS() as search_client:
                results = list(search_client.text(query, max_results=max_results))
        except Exception as exc:
            return f"Web search failed: {exc}"

        if not results:
            return "No web results found."

        return "\n".join(
            _format_search_result(index, result)
            for index, result in enumerate(results, 1)
        )

    return web_search


def _build_unavailable_search_tool(reason: str) -> BaseTool:
    @tool("web_search", args_schema=WebSearchInput)
    def web_search(query: str) -> str:
        """Explain why web search is unavailable."""
        return f"Web search is unavailable for query {query!r}. {reason}"

    return web_search


def _load_ddgs() -> Any:
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS
    return DDGS


def _format_search_result(index: int, result: dict[str, Any]) -> str:
    title = result.get("title") or "Untitled"
    url = result.get("href") or result.get("url") or ""
    snippet = result.get("body") or result.get("snippet") or ""
    return f"{index}. {title}\n   URL: {url}\n   Summary: {snippet}"
