#!/usr/bin/env python3
"""
Weather CLI using Open-Meteo (free, no API key).

Provides current, daily, forecast and hourly weather via subcommands.
"""

import argparse
import json
import sys

import requests


def geocode_location(query: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    r = requests.get(
        url,
        params={"name": query, "count": 1, "language": "zh", "format": "json"},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    results = data.get("results", [])
    if not results:
        return None
    loc = results[0]
    return loc["latitude"], loc["longitude"], loc.get("name", query), loc.get("country", "")


def wind_dir(deg) -> str:
    if deg is None:
        return "未知"
    dirs = ["北", "东北", "东", "东南", "南", "西南", "西", "西北", "北"]
    idx = round(deg / 45) % 8
    return dirs[idx]


def fmt_time(iso: str) -> str:
    """Extract HH:MM from an ISO datetime string."""
    if iso and len(iso) >= 16:
        return iso[11:16]
    return iso or ""


def fetch_weather(lat: float, lon: float, forecast_days: int = 2, forecast_hours: int = 0):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,is_day,precipitation,rain,showers,snowfall,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,daylight_duration,sunshine_duration,precipitation_sum,precipitation_hours,precipitation_probability_max,wind_speed_10m_max,wind_direction_10m_dominant",
        "timezone": "auto",
        "forecast_days": forecast_days,
    }
    if forecast_hours:
        params["hourly"] = "temperature_2m,apparent_temperature,relative_humidity_2m,weather_code,precipitation_probability,precipitation,rain,showers,snowfall,cloud_cover,pressure_msl,surface_pressure,wind_speed_10m,wind_direction_10m,wind_gusts_10m,is_day"
        params["forecast_hours"] = forecast_hours
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


WMO_CODE = {
    0: "晴",
    1: "大部晴朗",
    2: "多云",
    3: "阴",
    45: "雾",
    48: "雾凇",
    51: "毛毛雨",
    53: "小雨",
    55: "中雨",
    56: "冻毛毛雨",
    57: "冻雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    66: "冻雨",
    67: "冻雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    77: "雪粒",
    80: "阵雨",
    81: "强阵雨",
    82: "暴雨",
    85: "阵雪",
    86: "强阵雪",
    95: "雷雨",
    96: "雷雨伴冰雹",
    99: "强雷雨伴冰雹",
}


def weather_desc(code: int) -> str:
    return WMO_CODE.get(code, f"天气代码{code}")


def require_location(args):
    if not args.location:
        print("请使用 --location 指定城市")
        sys.exit(1)


def _location(args):
    geo = geocode_location(args.location)
    if geo is None:
        print(f"未找到地点：{args.location}")
        sys.exit(1)
    return geo


def _output(args, data: dict):
    if args.format == "json":
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(data["text"])


def cmd_now(args):
    require_location(args)
    lat, lon, name, country = _location(args)
    data = fetch_weather(lat, lon)
    cur = data["current"]
    result = {
        "location": name,
        "country": country,
        "time": cur.get("time"),
        "weather": weather_desc(cur["weather_code"]),
        "temperature_c": cur["temperature_2m"],
        "apparent_temperature_c": cur["apparent_temperature"],
        "humidity_percent": cur["relative_humidity_2m"],
        "precipitation_mm": cur["precipitation"],
        "rain_mm": cur["rain"],
        "showers_mm": cur["showers"],
        "snowfall_cm": cur["snowfall"],
        "cloud_cover_percent": cur["cloud_cover"],
        "pressure_hpa": cur["surface_pressure"],
        "wind_direction_deg": cur["wind_direction_10m"],
        "wind_direction": wind_dir(cur["wind_direction_10m"]),
        "wind_speed_kmh": cur["wind_speed_10m"],
        "wind_gusts_kmh": cur["wind_gusts_10m"],
        "is_day": bool(cur["is_day"]),
    }
    day_night = "白天" if result["is_day"] else "夜间"
    result["text"] = (
        f"{name} {day_night}实况：{result['weather']}, "
        f"气温 {result['temperature_c']}°C (体感 {result['apparent_temperature_c']}°C), "
        f"湿度 {result['humidity_percent']}%\n"
        f"降水 {result['precipitation_mm']}mm (雨{result['rain_mm']}/阵雨{result['showers_mm']}/雪{result['snowfall_cm']}cm), "
        f"气压 {result['pressure_hpa']}hPa, 云量 {result['cloud_cover_percent']}%\n"
        f"风向 {result['wind_direction']} {result['wind_speed_kmh']}km/h, "
        f"阵风 {result['wind_gusts_kmh']}km/h"
    )
    _output(args, result)


def cmd_today(args):
    require_location(args)
    lat, lon, name, country = _location(args)
    data = fetch_weather(lat, lon)
    daily = data["daily"]
    i = 0
    date = daily["time"][i]
    result = {
        "location": name,
        "country": country,
        "date": date,
        "weather": weather_desc(daily["weather_code"][i]),
        "temperature_max_c": daily["temperature_2m_max"][i],
        "temperature_min_c": daily["temperature_2m_min"][i],
        "apparent_temperature_max_c": daily["apparent_temperature_max"][i],
        "apparent_temperature_min_c": daily["apparent_temperature_min"][i],
        "precipitation_probability_max_percent": daily["precipitation_probability_max"][i],
        "precipitation_sum_mm": daily["precipitation_sum"][i],
        "precipitation_hours": daily["precipitation_hours"][i],
        "wind_direction_deg": daily["wind_direction_10m_dominant"][i],
        "wind_direction": wind_dir(daily["wind_direction_10m_dominant"][i]),
        "wind_speed_max_kmh": daily["wind_speed_10m_max"][i],
        "sunrise": fmt_time(daily["sunrise"][i]),
        "sunset": fmt_time(daily["sunset"][i]),
        "daylight_duration_seconds": daily["daylight_duration"][i],
        "sunshine_duration_seconds": daily["sunshine_duration"][i],
    }
    result["text"] = (
        f"{name}{f' ({country})' if country else ''} {date} 天气：{result['weather']}\n"
        f"温度 {result['temperature_min_c']}°C ~ {result['temperature_max_c']}°C "
        f"(体感 {result['apparent_temperature_min_c']}°C ~ {result['apparent_temperature_max_c']}°C)\n"
        f"降水概率 {result['precipitation_probability_max_percent']}%, "
        f"总降水 {result['precipitation_sum_mm']}mm, 降水时数 {result['precipitation_hours']}h\n"
        f"风向 {result['wind_direction']} 最高 {result['wind_speed_max_kmh']}km/h\n"
        f"日出 {result['sunrise']}, 日落 {result['sunset']}"
    )
    _output(args, result)


def cmd_forecast(args):
    require_location(args)
    lat, lon, name, country = _location(args)
    days = args.days
    data = fetch_weather(lat, lon, forecast_days=days)
    daily = data["daily"]
    items = []
    for i in range(days):
        item = {
            "date": daily["time"][i],
            "weather": weather_desc(daily["weather_code"][i]),
            "temperature_max_c": daily["temperature_2m_max"][i],
            "temperature_min_c": daily["temperature_2m_min"][i],
            "apparent_temperature_max_c": daily["apparent_temperature_max"][i],
            "apparent_temperature_min_c": daily["apparent_temperature_min"][i],
            "precipitation_probability_max_percent": daily["precipitation_probability_max"][i],
            "precipitation_sum_mm": daily["precipitation_sum"][i],
            "wind_direction": wind_dir(daily["wind_direction_10m_dominant"][i]),
            "wind_speed_max_kmh": daily["wind_speed_10m_max"][i],
            "sunrise": fmt_time(daily["sunrise"][i]),
            "sunset": fmt_time(daily["sunset"][i]),
        }
        items.append(item)
    result = {
        "location": name,
        "country": country,
        "days": days,
        "forecast": items,
    }
    lines = [
        f"{name}{f' ({country})' if country else ''} 未来 {days} 天天气预报：",
    ]
    for item in items:
        lines.append(
            f"{item['date']} {item['weather']} "
            f"{item['temperature_min_c']}°C ~ {item['temperature_max_c']}°C "
            f"(体感 {item['apparent_temperature_min_c']}°C ~ {item['apparent_temperature_max_c']}°C), "
            f"降水概率 {item['precipitation_probability_max_percent']}%, "
            f"风 {item['wind_direction']} {item['wind_speed_max_kmh']}km/h"
        )
    result["text"] = "\n".join(lines)
    _output(args, result)


def cmd_hourly(args):
    require_location(args)
    lat, lon, name, country = _location(args)
    hours = args.hours
    data = fetch_weather(lat, lon, forecast_hours=hours)
    hourly = data["hourly"]
    items = []
    # Sample every 3 hours to keep output readable in text mode.
    step = 3
    for i in range(0, hours, step):
        item = {
            "time": hourly["time"][i],
            "weather": weather_desc(hourly["weather_code"][i]),
            "temperature_c": hourly["temperature_2m"][i],
            "apparent_temperature_c": hourly["apparent_temperature"][i],
            "humidity_percent": hourly["relative_humidity_2m"][i],
            "precipitation_probability_percent": hourly["precipitation_probability"][i],
            "precipitation_mm": hourly["precipitation"][i],
            "cloud_cover_percent": hourly["cloud_cover"][i],
            "pressure_hpa": hourly["surface_pressure"][i],
            "wind_direction": wind_dir(hourly["wind_direction_10m"][i]),
            "wind_speed_kmh": hourly["wind_speed_10m"][i],
            "wind_gusts_kmh": hourly["wind_gusts_10m"][i],
            "is_day": bool(hourly["is_day"][i]),
        }
        items.append(item)
    result = {
        "location": name,
        "country": country,
        "hours": hours,
        "sample_step_hours": step,
        "hourly": items,
    }
    lines = [f"{name}{f' ({country})' if country else ''} 未来 {hours} 小时天气（每{step}小时）："]
    for item in items:
        lines.append(
            f"{item['time']} {item['weather']} {item['temperature_c']}°C "
            f"(体感 {item['apparent_temperature_c']}°C), "
            f"降水概率 {item['precipitation_probability_percent']}%, "
            f"风 {item['wind_direction']} {item['wind_speed_kmh']}km/h"
        )
    result["text"] = "\n".join(lines)
    _output(args, result)


def main():
    parser = argparse.ArgumentParser(prog="weather")
    sub = parser.add_subparsers(dest="command")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--location", required=True, help="城市名称")
    common.add_argument("--format", choices=["text", "json"], default="text", help="输出格式")

    p = sub.add_parser("now", parents=[common])
    p.set_defaults(func=cmd_now)

    p = sub.add_parser("today", parents=[common])
    p.set_defaults(func=cmd_today)

    p = sub.add_parser("forecast", parents=[common])
    p.add_argument("--days", type=int, default=3, help="预报天数（1-16）")
    p.set_defaults(func=cmd_forecast)

    p = sub.add_parser("hourly", parents=[common])
    p.add_argument("--hours", type=int, default=24, help="预报小时数（1-120）")
    p.set_defaults(func=cmd_hourly)

    args = parser.parse_args()
    if not getattr(args, "func", None):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
