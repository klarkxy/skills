# hermes-skills

个人自用的 Hermes / skills.sh 聚合技能仓库。

## 安装

仓库是把多个 skill 聚合在一起，但不需要全部安装。可以单独安装某一个 skill：

```bash
npx skills add klarkxy/skills@chinese-calendar
npx skills add klarkxy/skills@weather
```

也可以一次安装整个仓库（会安装所有 skill，不推荐）：

```bash
npx skills add klarkxy/skills
```

## 技能列表

| 技能 | 说明 |
|------|------|
| [chinese-calendar](skills/chinese-calendar/) | 中国农历/日程工具：农历转换、节假日查询、日程提醒 |
| [weather](skills/weather/) | 天气预报：基于 Open-Meteo，需指定 `--location` |

## 使用

安装后，在 Hermes 中直接使用 `:calendar` 或 `:weather` 命令。
