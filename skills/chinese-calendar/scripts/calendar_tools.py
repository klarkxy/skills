#!/usr/bin/env python3
"""
Chinese calendar utilities: lunar/solar conversion, holiday/workday check.
"""

from datetime import date, datetime
from typing import Optional, Tuple
import chinese_calendar as cc
from zhdate import ZhDate

CN_MONTH = ["正月", "二月", "三月", "四月", "五月", "六月",
            "七月", "八月", "九月", "十月", "冬月", "腊月"]
CN_DAY = ["初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
          "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
          "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"]


def solar_to_lunar_str(d: date) -> str:
    """Return Chinese lunar date string for a solar date."""
    z = ZhDate.from_datetime(datetime(d.year, d.month, d.day))
    leap = "闰" if z.lunar_month == z.leap_month else ""
    return f"{z.lunar_year}年{leap}{CN_MONTH[z.lunar_month - 1]}{CN_DAY[z.lunar_day - 1]}"


def lunar_to_solar(year: int, month: int, day: int, leap: bool = False) -> Optional[date]:
    """Convert lunar date to solar date. Returns None if invalid (e.g. leap month does not exist)."""
    try:
        z = ZhDate(year, month, day, leap_month=leap)
        return z.to_datetime().date()
    except Exception:
        return None


def holiday_info(d: date) -> Tuple[bool, Optional[str], bool]:
    """Return (is_holiday, holiday_name, is_workday)."""
    is_holiday, name = cc.get_holiday_detail(d)
    workday = cc.is_workday(d)
    return is_holiday, name, workday


def today_info() -> str:
    """Formatted info for today."""
    d = date.today()
    lunar = solar_to_lunar_str(d)
    is_holiday, name, workday = holiday_info(d)
    lines = [f"今天：{d}", f"农历：{lunar}"]
    if is_holiday:
        lines.append(f"节假日：{name}")
    else:
        lines.append(f"状态：{'工作日' if workday else '休息日'}")
    return "\n".join(lines)
