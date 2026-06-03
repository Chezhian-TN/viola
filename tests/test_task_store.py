from viola.tools.task_store import TaskStore


def test_task_store_adds_and_completes_task(tmp_path) -> None:
    store = TaskStore(tmp_path)
    task = store.add_task(title="Review roadmap", due_date="2026-06-05", priority="high")

    assert task["status"] == "open"
    assert store.list_tasks(status="open")[0]["id"] == task["id"]

    completed = store.complete_task(task_id=task["id"])

    assert completed is not None
    assert completed["status"] == "done"
    assert completed["completed_at"] is not None


def test_task_store_filters_meetings_by_date(tmp_path) -> None:
    store = TaskStore(tmp_path)
    store.add_meeting(
        title="Product Sync",
        start_time="2026-06-03T10:00:00+05:30",
        duration_minutes=45,
        attendees=["Mira", "Dev"],
    )
    store.add_meeting(
        title="Design Review",
        start_time="2026-06-04T10:00:00+05:30",
        duration_minutes=30,
    )

    meetings = store.list_meetings(date="2026-06-03")

    assert len(meetings) == 1
    assert meetings[0]["title"] == "Product Sync"

