"""
Scheduler: expand repeating events and compute reminders.
"""

from datetime import date, timedelta
from typing import List, Optional, Tuple
from events import Event


def next_occurrence(event: Event, from_date: date) -> Optional[date]:
    """Return the next occurrence of an event on or after from_date."""
    try:
        base = date.fromisoformat(event.date)
    except (ValueError, TypeError):
        return None

    if event.repeat == "none":
        return base if base >= from_date else None

    if event.repeat == "yearly":
        for year in range(from_date.year, from_date.year + 2):
            d = date(year, base.month, base.day)
            if d >= from_date:
                return d
        return None

    if event.repeat == "monthly":
        y, m = from_date.year, from_date.month
        for _ in range(24):
            try:
                d = date(y, m, base.day)
            except ValueError:
                d = date(y, m, 28)
            if d >= from_date:
                return d
            m += 1
            if m > 12:
                m = 1
                y += 1
        return None

    if event.repeat == "weekly":
        d = base
        while d < from_date:
            d += timedelta(days=7)
        return d

    if event.repeat == "daily":
        return from_date

    return None


def upcoming_events(events: List[Event], from_date: date, max_days: int) -> List[Tuple[int, Event, date]]:
    """List events occurring within max_days from from_date, sorted by days remaining."""
    result = []
    for e in events:
        if e.done:
            continue
        occ = next_occurrence(e, from_date)
        if occ is None:
            continue
        delta = (occ - from_date).days
        if delta <= max_days:
            result.append((delta, e, occ))
    result.sort(key=lambda x: (x[0], x[1].title))
    return result


def check_reminders(events: List[Event], today: date) -> List[Tuple[int, Event, date]]:
    """Return events that should be reminded today, based on remind_days_before."""
    result = []
    for e in events:
        if e.done:
            continue
        occ = next_occurrence(e, today)
        if occ is None:
            continue
        delta = (occ - today).days
        if delta in e.remind_days_before:
            result.append((delta, e, occ))
    result.sort(key=lambda x: x[0])
    return result
