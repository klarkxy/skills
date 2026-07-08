#!/usr/bin/env python3
"""
Weather CLI using Open-Meteo (free, no API key).
"""

import argparse
import sys
from datetime import datetime

import requests

# Default location: Xinchang, Shaoxing, Zhejiang
DEFAULT_LAT = 29.4998
DEFAULT_LON = 120.9040


def geocode_location(query: str):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    r = requests.get(url, params={"name": query, "count": 1, "language": "zh", "format": "json"}, timeout=10)
    r.raise_for_status()
    data = r.json()
    results = data.get("results", [])
    if not results:
        return None
    loc = results[0]
    return loc["latitude"], loc["longitude"], loc.get("name", query), loc.get("country", "")


def fetch_weather(lat: float, lon: float):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,weather_code",
        "timezone": "auto",
        "forecast_days": 2,
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


WMO_CODE = {
    0: "晴", 1: "大部晴朗", 2: "多云", 3: "阴",
    45: "雾", 48: "雾凇",
    51: "毛毛雨", 53: "小雨", 55: "中雨",
    56: "冻毛毛雨", 57: "冻雨",
    61: "小雨", 63: "中雨", 65: "大雨",
    66: "冻雨", 67: "冻雨",
    71: "小雪", 73: "中雪", 75: "大雪",
    77: "雪粒",
    80: "阵雨", 81: "强阵雨", 82: "暴雨",
    85: "阵雪", 86: "强阵雪",
    95: "雷雨", 96: "雷雨伴冰雹", 99: "强雷雨伴冰雹",
}


def weather_desc(code: int) -> str:
    return WMO_CODE.get(code, f"天气代码{code}")


def cmd_now(args):
    data = fetch_weather(DEFAULT_LAT, DEFAULT_LON)
    cur = data["current"]
    loc = "绍兴新昌"
    print(f"{loc} 当前天气：{weather_desc(cur['weather_code'])}, {cur['temperature_2m']}°C, 湿度{cur['relative_humidity_2m']}%, 风速{cur['wind_speed_10m']}km/h")


def cmd_today(args):
    query = args.location or "绍兴新昌"
    geo = geocode_location(query)
    if geo is None:
        print(f"未找到地点：{query}")
        return
    lat, lon, name, country = geo
    data = fetch_weather(lat, lon)
    daily = data["daily"]
    today_idx = 0
    print(f"{name}{f' ({country})' if country else ''} 今日天气：{weather_desc(daily['weather_code'][today_idx])}, 最高 {daily['temperature_2m_max'][today_idx]}°C, 最低 {daily['temperature_2m_min'][today_idx]}°C")


def main():
    parser = argparse.ArgumentParser(prog="weather")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("now")
    p.set_defaults(func=cmd_now)

    p = sub.add_parser("today")
    p.add_argument("--location", default="绍兴新昌")
    p.set_defaults(func=cmd_today)

    args = parser.parse_args()
    if not getattr(args, "func", None):
        parser.print_help()
        sys.exit(1)
    args.func(args)


if __name__ == "__main__":
    main()
