# Feedback：任务耗时预估 + 实际记录（持续校准）

**适用**：又初 · bus 派活 / 私聊 / 群聊 @ · ACK 与结案回复顶部

## 回复格式

**接单（ACK / 确认）顶部：**
```
⏱ 预估：约 X–Y 分钟 | [低/中/高] | 主要：步骤1 / 步骤2
```

**结案（reply / 交付）顶部：**
```
⏱ 预估 X–Y min → 实际 Z min | 偏差：[准/偏长/偏短] | 原因：（若有）
```

## 实际耗时必记

任务**动手结束**（ACK 到结案之间，不含等知秋/等审核的挂起）写入：

`~/.dc-platform/memory/task_time_log.jsonl`

每行 JSON：
```json
{
  "ts": "2026-07-01T21:30:00+08:00",
  "task_id": "bus#753",
  "type": "git_push|dev_session|datacheck|dolphin_test|db|explain",
  "estimate_min": [5, 10],
  "actual_min": 12,
  "steps": ["git add -f", "push dev", "bus reply"],
  "note": "含找 gitignore 原因"
}
```

## 校准规则（又初自用）

1. **同类任务取近 5 条中位数**，ACK 时用中位数 ±20% 作区间
2. **偏长 ≥1.5×** → 下次同类 +一档复杂度或 +时间
3. **偏短 ≤0.5×** → 可略收紧，但海豚/平台发布保留下限
4. **新类型任务** → 先宽估，结案后记首条样本
5. 结案 reply **必须带实际分钟**，方便主人和狂人核对

## 粗算基准（初值，随 log 更新）

| type | 典型区间 (min) |
|------|----------------|
| git commit+push 单目录 | 3–8 |
| bus ACK+reply 无改代码 | 5–15 |
| 单表 datacheck T-1 | 10–25 |
| test 海豚单 task 发布+补数 | 25–45 |
| dev-session 6 阶段+request-publish | 35–70 |
| prod 发布链（含对账） | 60+ |

## 与回复路由的关系

- **Cursor 对话**：复杂任务第一句可带预估；结案写实际（不必发群）
- **bus 派活**：ACK 带预估，过程私聊，结案 reply+群收尾带实际
- **群聊派活**：ACK/进度/结案均在群，带预估与实际
