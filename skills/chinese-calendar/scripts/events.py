"""
Event storage (JSON-backed).
"""

import json
import os
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union


@dataclass
class Event:
    id: str
    title: str
    date: str  # YYYY-MM-DD
    time: Optional[str] = None
    repeat: str = "none"  # none | daily | weekly | monthly | yearly
    remind_days_before: List[int] = field(default_factory=lambda: [0])
    done: bool = False
    created_at: Optional[str] = None


class EventStore:
    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        if not self.path.exists():
            self._save([])

    def _load(self) -> List[Event]:
        try:
            with self.path.open("r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid event data: {self.path}") from exc
        if not isinstance(data, dict) or not isinstance(data.get("events", []), list):
            raise ValueError(f"invalid event data: {self.path}")
        return [Event(**e) for e in data.get("events", [])]

    def _save(self, events: List[Event]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(f"{self.path.suffix}.tmp")
        with temporary_path.open("w", encoding="utf-8") as f:
            json.dump({"events": [asdict(e) for e in events]}, f, ensure_ascii=False, indent=2)
        os.replace(temporary_path, self.path)

    def add(self, title: str, date: str, time: Optional[str] = None,
            repeat: str = "none", remind_days_before: Optional[List[int]] = None) -> Event:
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"invalid date format: {date}, expected YYYY-MM-DD")
        if time:
            try:
                datetime.strptime(time, "%H:%M")
            except ValueError:
                raise ValueError(f"invalid time format: {time}, expected HH:MM")
        if repeat not in {"none", "daily", "weekly", "monthly", "yearly"}:
            raise ValueError(f"invalid repeat: {repeat}")
        events = self._load()
        if remind_days_before is None:
            remind_days_before = [0]
        if any(not isinstance(day, int) or isinstance(day, bool) or day < 0 for day in remind_days_before):
            raise ValueError("remind days must be non-negative")
        event = Event(
            id=str(uuid.uuid4())[:8],
            title=title,
            date=date,
            time=time,
            repeat=repeat,
            remind_days_before=remind_days_before,
            created_at=datetime.now().isoformat(timespec="seconds")
        )
        events.append(event)
        self._save(events)
        return event

    def list_all(self) -> List[Event]:
        return self._load()

    def remove(self, event_id: str) -> bool:
        events = self._load()
        new_events = [e for e in events if e.id != event_id]
        if len(new_events) == len(events):
            return False
        self._save(new_events)
        return True
