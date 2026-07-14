"""Small deterministic check for event persistence and reminder scheduling."""

from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from events import Event, EventStore
from scheduler import check_reminders, next_occurrence


def main() -> None:
    with TemporaryDirectory() as directory:
        store = EventStore(Path(directory) / "events.json")
        store.add("报名", "2027-01-16", remind_days_before=[0, 3])
        assert check_reminders(store.list_all(), date(2027, 1, 13))[0][0] == 3
        assert check_reminders(store.list_all(), date(2027, 1, 14)) == []
        assert check_reminders(store.list_all(), date(2027, 1, 16))[0][0] == 0

    leap_day = Event(id="leap", title="闰日", date="2024-02-29", repeat="yearly")
    assert next_occurrence(leap_day, date(2025, 1, 1)) == date(2028, 2, 29)

    future_daily = Event(id="future", title="未来", date="2026-12-28", repeat="daily")
    assert next_occurrence(future_daily, date(2026, 7, 14)) == date(2026, 12, 28)

    future_monthly = Event(id="future-month", title="未来月", date="2026-12-31", repeat="monthly")
    assert next_occurrence(future_monthly, date(2026, 7, 14)) == date(2026, 12, 31)

    future_yearly = Event(id="future-year", title="未来年", date="2027-12-28", repeat="yearly")
    assert next_occurrence(future_yearly, date(2026, 7, 14)) == date(2027, 12, 28)

    month_end = Event(id="month", title="月底", date="2026-01-31", repeat="monthly")
    assert next_occurrence(month_end, date(2026, 4, 1)) == date(2026, 4, 30)
    print("ok")


if __name__ == "__main__":
    main()
