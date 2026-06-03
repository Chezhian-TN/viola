from __future__ import annotations

from pathlib import Path

from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field

from viola.tools.task_store import JsonRecord, TaskStore


class ScheduleMeetingInput(BaseModel):
    title: str = Field(description="Meeting title.")
    start_time: str = Field(
        description="Meeting start time. Prefer ISO 8601, such as 2026-06-03T10:00:00+05:30."
    )
    duration_minutes: int = Field(default=30, ge=1, description="Meeting duration in minutes.")
    attendees: list[str] = Field(default_factory=list, description="People attending the meeting.")
    notes: str = Field(default="", description="Optional meeting notes.")


class ListMeetingsInput(BaseModel):
    date: str | None = Field(default=None, description="Optional date filter in YYYY-MM-DD format.")


class CreateTaskInput(BaseModel):
    title: str = Field(description="Task title.")
    due_date: str | None = Field(default=None, description="Optional due date or deadline.")
    priority: str = Field(default="normal", description="Task priority: low, normal, high, urgent.")
    notes: str = Field(default="", description="Optional task details.")


class ListTasksInput(BaseModel):
    status: str | None = Field(default=None, description="Optional status filter: open or done.")


class CompleteTaskInput(BaseModel):
    task_id: str = Field(description="ID of the task to mark done.")


def build_task_tools(data_dir: str | Path) -> list[BaseTool]:
    store = TaskStore(data_dir)

    @tool("schedule_meeting", args_schema=ScheduleMeetingInput)
    def schedule_meeting(
        title: str,
        start_time: str,
        duration_minutes: int = 30,
        attendees: list[str] | None = None,
        notes: str = "",
    ) -> str:
        """Schedule a meeting in Viola's local meeting store."""
        meeting = store.add_meeting(
            title=title,
            start_time=start_time,
            duration_minutes=duration_minutes,
            attendees=attendees or [],
            notes=notes,
        )
        return "Scheduled meeting:\n" + _format_meeting(meeting)

    @tool("list_meetings", args_schema=ListMeetingsInput)
    def list_meetings(date: str | None = None) -> str:
        """List meetings from Viola's local meeting store."""
        meetings = store.list_meetings(date=date)
        if not meetings:
            return "No meetings found."
        return "Meetings:\n" + "\n".join(_format_meeting(meeting) for meeting in meetings)

    @tool("create_task", args_schema=CreateTaskInput)
    def create_task(
        title: str,
        due_date: str | None = None,
        priority: str = "normal",
        notes: str = "",
    ) -> str:
        """Create a task in Viola's local task store."""
        task = store.add_task(title=title, due_date=due_date, priority=priority, notes=notes)
        return "Created task:\n" + _format_task(task)

    @tool("list_tasks", args_schema=ListTasksInput)
    def list_tasks(status: str | None = None) -> str:
        """List tasks from Viola's local task store."""
        tasks = store.list_tasks(status=status)
        if not tasks:
            return "No tasks found."
        return "Tasks:\n" + "\n".join(_format_task(task) for task in tasks)

    @tool("complete_task", args_schema=CompleteTaskInput)
    def complete_task(task_id: str) -> str:
        """Mark a task as done in Viola's local task store."""
        task = store.complete_task(task_id=task_id)
        if task is None:
            return f"No task found with ID {task_id!r}."
        return "Completed task:\n" + _format_task(task)

    return [schedule_meeting, list_meetings, create_task, list_tasks, complete_task]


def _format_meeting(meeting: JsonRecord) -> str:
    attendees = meeting.get("attendees") or []
    attendee_text = ", ".join(attendees) if attendees else "none"
    notes = f" Notes: {meeting['notes']}" if meeting.get("notes") else ""
    return (
        f"- {meeting['id']}: {meeting['title']} at {meeting['start_time']} "
        f"for {meeting['duration_minutes']} minutes. Attendees: {attendee_text}.{notes}"
    )


def _format_task(task: JsonRecord) -> str:
    due = f" Due: {task['due_date']}." if task.get("due_date") else ""
    notes = f" Notes: {task['notes']}" if task.get("notes") else ""
    return (
        f"- {task['id']}: {task['title']} "
        f"[{task['status']}, priority: {task['priority']}].{due}{notes}"
    )

