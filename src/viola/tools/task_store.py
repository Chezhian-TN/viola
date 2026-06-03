from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

JsonRecord = dict[str, Any]


class TaskStore:
    """Small JSON-backed store for local assistant tasks and meetings."""

    def __init__(self, data_dir: str | Path) -> None:
        self.data_dir = Path(data_dir)
        self.meetings_path = self.data_dir / "meetings.json"
        self.tasks_path = self.data_dir / "tasks.json"

    def add_meeting(
        self,
        *,
        title: str,
        start_time: str,
        duration_minutes: int,
        attendees: list[str] | None = None,
        notes: str = "",
    ) -> JsonRecord:
        if not title.strip():
            raise ValueError("Meeting title is required.")
        if duration_minutes <= 0:
            raise ValueError("Meeting duration must be greater than zero.")

        meeting = {
            "id": self._new_id("meet"),
            "title": title.strip(),
            "start_time": self._normalize_datetime_text(start_time),
            "duration_minutes": duration_minutes,
            "attendees": attendees or [],
            "notes": notes.strip(),
            "created_at": self._utc_now(),
        }
        meetings = self._read_rows(self.meetings_path)
        meetings.append(meeting)
        self._write_rows(self.meetings_path, meetings)
        return meeting

    def list_meetings(self, *, date: str | None = None) -> list[JsonRecord]:
        meetings = self._read_rows(self.meetings_path)
        if date:
            meetings = [
                meeting
                for meeting in meetings
                if str(meeting.get("start_time", "")).startswith(date)
            ]
        return sorted(meetings, key=lambda meeting: str(meeting.get("start_time", "")))

    def add_task(
        self,
        *,
        title: str,
        due_date: str | None = None,
        priority: str = "normal",
        notes: str = "",
    ) -> JsonRecord:
        if not title.strip():
            raise ValueError("Task title is required.")

        task = {
            "id": self._new_id("task"),
            "title": title.strip(),
            "due_date": due_date.strip() if due_date else None,
            "priority": priority.strip().lower() or "normal",
            "notes": notes.strip(),
            "status": "open",
            "created_at": self._utc_now(),
            "completed_at": None,
        }
        tasks = self._read_rows(self.tasks_path)
        tasks.append(task)
        self._write_rows(self.tasks_path, tasks)
        return task

    def list_tasks(self, *, status: str | None = None) -> list[JsonRecord]:
        tasks = self._read_rows(self.tasks_path)
        if status:
            normalized = status.strip().lower()
            tasks = [task for task in tasks if task.get("status") == normalized]
        return sorted(
            tasks,
            key=lambda task: (
                str(task.get("status", "")),
                str(task.get("due_date") or ""),
                str(task.get("created_at", "")),
            ),
        )

    def complete_task(self, *, task_id: str) -> JsonRecord | None:
        tasks = self._read_rows(self.tasks_path)
        for task in tasks:
            if task.get("id") == task_id:
                task["status"] = "done"
                task["completed_at"] = self._utc_now()
                self._write_rows(self.tasks_path, tasks)
                return task
        return None

    def _read_rows(self, path: Path) -> list[JsonRecord]:
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path} contains invalid JSON.") from exc
        if not isinstance(data, list):
            raise ValueError(f"{path} must contain a JSON list.")
        return data

    def _write_rows(self, path: Path, rows: list[JsonRecord]) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(f"{path.suffix}.tmp")
        temp_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        temp_path.replace(path)

    def _normalize_datetime_text(self, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("A start time is required.")
        try:
            parsed = datetime.fromisoformat(cleaned.replace("Z", "+00:00"))
        except ValueError:
            return cleaned
        return parsed.isoformat()

    def _new_id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:10]}"

    def _utc_now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

