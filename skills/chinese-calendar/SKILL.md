---
name: chinese-calendar
description: |
  中国农历/日程工具：支持农历转公历、公历转农历、节假日/工作日查询、日程添加与每日提醒。
  Chinese calendar & scheduling: lunar/solar conversion, holiday/workday check, event reminders.
metadata:
  author: klarkxy
  version: "0.1.0"
  argument-hint: <command>
---

# chinese-calendar

中国农历与日程管理工具，适合中文用户日常查询和轻量日程提醒。

## 安装

```bash
npx skills add klarkxy/skills@chinese-calendar
pip install -r <技能安装路径>/requirements.txt
```

## 使用

用 `scripts/calendar_cli.py` 运行命令。事件默认保存在本技能目录的 `data/events.json`，也可在命令前传入 `--data-file <path>`，或设置 `CHINESE_CALENDAR_DATA_FILE` 环境变量。

## 日历工具

- `:calendar today`
  - 显示今日公历、农历、节假日/工作日状态。
- `:calendar solar-to-lunar --date <YYYY-MM-DD>`
  - 公历转农历。
- `:calendar lunar-to-solar --year <年> --month <月> --day <日> [--leap]`
  - 农历转公历。`--leap` 表示闰月。
- `:calendar holiday --date <YYYY-MM-DD>`
  - 查询某天是否节假日、是否工作日。

## 日程工具

- `:calendar event add --title <标题> --date <YYYY-MM-DD> [--time HH:MM] [--repeat none|daily|weekly|monthly|yearly] [--remind 0,1,3]`
  - 添加日程。`--remind` 是逗号分隔的提前天数，默认 `0`。
- `:calendar event list [--days N]`
  - 列出未来 N 天（默认 7）的日程。
- `:calendar event next`
  - 显示最近的日程。
- `:calendar event remove --id <ID>`
  - 删除日程。
- `:calendar event check [--date YYYY-MM-DD]`
  - 输出当天需要提醒的日程；`--date` 用于测试或补跑。

## 数据存储

日程默认保存在本技能目录的 `data/events.json`。写入采用临时文件替换，避免中断时损坏数据。

## 每日提醒 cron

每天只运行一次 `event check`。有输出才推送，无输出不发消息；重复运行会重复输出同一提醒。

```yaml
schedule: "0 9 * * *"
deliver: origin
prompt: "运行 <技能安装路径>/scripts/calendar_cli.py event check；如果输出不为空就把结果发给我。"
```

将 `<技能安装路径>` 替换为本地实际路径。
