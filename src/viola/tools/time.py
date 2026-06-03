from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field


class LocalTimeInput(BaseModel):
    timezone_name: str | None = Field(
        default=None,
        description="IANA timezone name, such as Asia/Calcutta or America/New_York.",
    )


def build_time_tools(default_timezone: str) -> list[BaseTool]:
    @tool("get_local_time", args_schema=LocalTimeInput)
    def get_local_time(timezone_name: str | None = None) -> str:
        """Return the current local date and time for a timezone."""
        requested_timezone = timezone_name or default_timezone
        try:
            timezone = ZoneInfo(requested_timezone)
        except ZoneInfoNotFoundError:
            return (
                f"Unknown timezone {requested_timezone!r}. "
                "Use an IANA timezone like Asia/Calcutta or America/New_York."
            )
        now = datetime.now(timezone)
        return f"{requested_timezone}: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}"

    return [get_local_time]

