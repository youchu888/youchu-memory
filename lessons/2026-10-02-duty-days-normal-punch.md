---
date: 2026-10-02
tags: [onehr, punch, duty, holiday]
severity: high
domain: ops
---

# 值班日即使法定假也要正常打卡

## 主人定调（2026-10-02）

**2026-10-03、2026-10-05** 值班 → 正常打卡（国庆连休中）。

## 正确做法

- 登记：`omdb/tgbot/data/personal_duty_dates.json`（脚本 `scripts/set_duty_day.py`）
- `should_skip_punch`：值班日 **不跳**（覆盖法定假/周日）
- 居家抽查跟打卡；绿点仍跟打卡窗
- 日报/学习：`should_skip_non_workday_automation` **仍按假日 skip**（值班≠要写日报）

## 验证

```bash
python3 omdb/tgbot/scripts/set_duty_day.py --check 2026-10-03
# punch_skip=false reason=duty:…；report_skip=true
```
