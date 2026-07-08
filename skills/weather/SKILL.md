---
name: weather
description: 获取当地天气预报。基于 Open-Meteo，无需 API key。
metadata:
  author: klarkxy
  version: "0.1.0"
  argument-hint: <command>
---

# weather

获取当地天气预报，数据来源于 Open-Meteo，无需 API key。

## 安装

```bash
npx skills add klarkxy/skills@weather
```

安装后在 Hermes 使用的 Python 环境中安装依赖：

```bash
pip install -r ~/.hermes/skills/weather/requirements.txt
```

> 注意：Windows 下路径通常为 `C:/Users/<你的用户名>/.hermes/skills/weather`，请根据实际安装路径替换。

## 使用

```bash
python weather_cli.py <command> --location <城市> [--format text|json]
```

- `:weather now --location <城市>`
  - 当前实况天气：气温、体感温度、湿度、降水、气压、云量、风向风速、阵风、白天/夜间。
- `:weather today --location <城市>`
  - 今日天气：天气、温度区间、体感温度、降水概率/量、风向风速、日出日落。
- `:weather forecast --location <城市> [--days N]`
  - 未来 N 天天气预报（默认 3 天）。
- `:weather hourly --location <城市> [--hours N]`
  - 未来 N 小时逐 3 小时采样天气（默认 24 小时）。

所有命令都支持 `--format json` 输出原始数据。

## 数据来源

- Open-Meteo: https://open-meteo.com/
