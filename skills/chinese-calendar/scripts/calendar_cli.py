#!/usr/bin/env python3
"""
CLI entry point for chinese-calendar skill.
"""

import argparse
import os
import sys
from datetime import date
from pathlib import Path

# Allow running this script directly from the scripts directory
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from events import EventStore
from scheduler import upcoming_events, check_reminders, next_occurrence
from calendar_tools import (
    solar_to_lunar_str, lunar_to_solar, holiday_info, today_info
)

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "events.json"


def get_store(args) -> EventStore:
    return EventStore(args.data_file)


def parse_date(value: str) -> str:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("日期必须是 YYYY-MM-DD") from exc
    return value


def parse_remind_days(value: str):
    try:
        days = sorted({int(item.strip()) for item in value.split(",") if item.strip()})
    except ValueError as exc:
        raise ValueError("提醒天数必须是非负整数") from exc
    if not days or any(day < 0 for day in days):
        raise ValueError("提醒天数必须是非负整数")
    return days


def cmd_lunar_to_solar(args):
    d = lunar_to_solar(args.year, args.month, args.day, args.leap)
    if d is None:
        leap = "闰" if args.leap else ""
        print(f"无法将 {args.year}年{leap}{args.month}月{args.day}日 转换为公历")
        return
    leap = "闰" if args.leap else ""
    print(f"{args.year}年{leap}{args.month}月{args.day}日 -> {d}")


def cmd_solar_to_lunar(args):
    d = date.fromisoformat(args.date)
    print(f"{d} -> {solar_to_lunar_str(d)}")


def cmd_today(args):
    print(today_info())


def cmd_holiday(args):
    d = date.fromisoformat(args.date)
    is_holiday, name, workday = holiday_info(d)
    if is_holiday:
        print(f"{d} 是节假日：{name}")
    else:
        print(f"{d} 不是节假日，{'工作日' if workday else '休息日'}")


def cmd_event_add(args):
    try:
        e = get_store(args).add(
            title=args.title,
            date=args.date,
            time=args.time,
            repeat=args.repeat,
            remind_days_before=parse_remind_days(args.remind),
        )
    except ValueError as exc:
        raise SystemExit(f"错误：{exc}")
    print(f"已添加：{e.title} {e.date} {e.time or ''} [ID: {e.id}]")


def cmd_event_list(args):
    today = date.today()
    events = upcoming_events(get_store(args).list_all(), today, args.days)
    if not events:
        print(f"未来 {args.days} 天没有日程")
        return
    for delta, e, occ in events:
        prefix = "今天" if delta == 0 else f"{delta} 天后"
        print(f"{prefix} ({occ}) {e.title} {e.time or ''} [ID: {e.id}]")


def cmd_event_next(args):
    today = date.today()
    candidates = []
    for e in get_store(args).list_all():
        if e.done:
            continue
        occ = next_occurrence(e, today)
        if occ:
            candidates.append(((occ - today).days, e, occ))
    if not candidates:
        print("没有待办日程")
        return
    candidates.sort(key=lambda x: x[0])
    delta, e, occ = candidates[0]
    print(f"最近日程：{e.title} {occ} {e.time or ''}，还有 {delta} 天 [ID: {e.id}]")


def cmd_event_remove(args):
    if get_store(args).remove(args.id):
        print(f"已删除事件 {args.id}")
    else:
        print(f"未找到事件 {args.id}")


def cmd_event_check(args):
    today = date.fromisoformat(args.date) if args.date else date.today()
    reminders = check_reminders(get_store(args).list_all(), today)
    if not reminders:
        return
    print("日程提醒：")
    for delta, e, occ in reminders:
        if delta == 0:
            print(f"今天 {e.time or ''}: {e.title}")
        else:
            print(f"{delta} 天后 ({occ}): {e.title}")


def main():
    parser = argparse.ArgumentParser(prog="calendar")
    parser.add_argument(
        "--data-file",
        default=os.environ.get("CHINESE_CALENDAR_DATA_FILE", str(DEFAULT_DATA_PATH)),
        help="事件 JSON 文件路径，默认使用本技能目录下的 data/events.json",
    )
    sub = parser.add_subparsers(dest="command")

    # Calendar tools
    p = sub.add_parser("lunar-to-solar")
    p.add_argument("--year", type=int, required=True)
    p.add_argument("--month", type=int, required=True)
    p.add_argument("--day", type=int, required=True)
    p.add_argument("--leap", action="store_true")
    p.set_defaults(func=cmd_lunar_to_solar)

    p = sub.add_parser("solar-to-lunar")
    p.add_argument("--date", required=True, type=parse_date)
    p.set_defaults(func=cmd_solar_to_lunar)

    p = sub.add_parser("today")
    p.set_defaults(func=cmd_today)

    p = sub.add_parser("holiday")
    p.add_argument("--date", required=True, type=parse_date)
    p.set_defaults(func=cmd_holiday)

    # Event tools
    event = sub.add_parser("event")
    event_sub = event.add_subparsers(dest="event_command")

    p = event_sub.add_parser("add")
    p.add_argument("--title", required=True)
    p.add_argument("--date", required=True, type=parse_date)
    p.add_argument("--time")
    p.add_argument("--repeat", default="none",
                    choices=["none", "daily", "weekly", "monthly", "yearly"])
    p.add_argument("--remind", default="0", help="逗号分隔的提前天数，例如 '0,3,7'")
    p.set_defaults(func=cmd_event_add)

    p = event_sub.add_parser("list")
    p.add_argument("--days", type=int, default=7)
    p.set_defaults(func=cmd_event_list)

    p = event_sub.add_parser("next")
    p.set_defaults(func=cmd_event_next)

    p = event_sub.add_parser("remove")
    p.add_argument("--id", required=True)
    p.set_defaults(func=cmd_event_remove)

    p = event_sub.add_parser("check")
    p.add_argument("--date", type=parse_date, help="用于测试或补跑的日期，格式 YYYY-MM-DD")
    p.set_defaults(func=cmd_event_check)

    args = parser.parse_args()
    if not getattr(args, "func", None):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
