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

安装后在 Hermes 使用的 Python 环境中安装依赖：

```bash
pip install -r C:/Users/27837/.hermes/skills/weather/requirements.txt
```

> 注意：路径请根据你的 Hermes skill 安装路径调整。

## 使用

- `:weather today --location <城市>`
  - 查询今日天气。必须指定城市。
- `:weather now --location <城市>`
  - 查询当前实况天气。必须指定城市。

## 数据来源

- Open-Meteo: https://open-meteo.com/
