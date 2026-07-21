---
date: 2026-06-13
tags: [dolphin, schedule, video, dependent, test, publish]
severity: high
domain: ops
---

# 海豚 wf 发布后 schedule 仍 OFFLINE，下游 DEPENDENT 永久挂起

## 背景

`wf_视频事件_小时`（schedule id=95）v5 发布后，上游 schedule 变 OFFLINE，下游 `wf_视频汇总_小时` 每小时仍触发，DEPENDENT `等_视频事件_小时` 轮询 currentHour 直至人工 STOP，持续 10h+。

## 坑 / 错误做法

1. **只把 wf 设回 ONLINE，不恢复 schedule** — DS 行为：wf OFFLINE 时 schedule 联动 OFFLINE；wf 再 ONLINE **不会**自动把 schedule 拉回 ONLINE。
2. **`set_workflow_global_params` / `remove_task_from_workflow` 缺第 5 步** — 仅 OFFLINE→PUT→ONLINE，未 `online_schedule`；`publish_task_sql` 已有此步，但改 globalParams 的路径没有。
3. **发布 SQL 切源但未配齐 globalParams** — v4 改用 `dw_user_event_detail_new` + `dt` 过滤，wf 级 `hour_start_time`/`dt_partition*` 为空，任务秒失败。
4. **仓库 SQL 与海豚不一致** — 下次从 repo 发布会回退旧源表、缺 `dt` 剪枝。

## 正确做法

1. **任何 wf PUT 后必查 schedule**：`GET schedules?wf_code=...`，若 `releaseState=OFFLINE` 则 `POST schedules/{id}/online`。
2. **小时视频任务 globalParams 模板**（与 `wf_广告渠道扣量_小时` 对齐）：
   - `hour_start_time` = `$[yyyy-MM-dd HH:00:00-3/24]`
   - `hour_start_time1/2/3` = `-1/24`、`-2/24`、`-3/24`
   - `hour_end_time` = `$[yyyy-MM-dd HH:00:00]`
   - `dt_partition1/2/3` = `$[yyyy-MM-dd-1/24]` 等
   - `hour_partition1/2/3` 由 task localParams 提供（`$[yyyyMMddHH-1/24]` 等）
3. **补数顺序**：先上游 `wf_视频事件_小时` complement → 再下游从 `dwm_video_event_h` 节点 `START_PROCESS`（跳过 DEPENDENT）。
4. **代码层**：`dolphin_client.set_workflow_global_params` / `remove_task_from_workflow` 在 wf 恢复 ONLINE 后，若发布前 schedule 为 ONLINE，自动 `online_schedule`（与 `dolphin_writer.publish_task_sql` 一致）。

## 验证

```bash
# schedule 双 ONLINE
curl .../schedules?wf_code=21869808631296  # releaseState=ONLINE
curl .../schedules?wf_code=21869819703040  # releaseState=ONLINE

# 无 RUNNING 卡 DEPENDENT
dolphin_get_running_summary → total=0

# 数据：dwd/dwm 近 24h 分区有行
SELECT DATE_FORMAT(hour,'%Y-%m-%d %H:00'), COUNT(*) FROM dwd.dwd_video_event_h
WHERE dt >= '2026-06-12' GROUP BY 1 ORDER BY 1;
```

## 关联

- 工作流：`wf_视频事件_小时` wf=21869808631296 schedule=95；`wf_视频汇总_小时` wf=21869819703040 schedule=98
- SQL：`ops_system/02.dwd/dwd_video_event_h/dwd_video_event_h_hourly.sql`
- 代码：`dc-platform-server/app/services/dolphin_client.py`（globalParams / remove_task）
- 发布 5 步规范：`vscode-extension/server-mcp/prompts/_dolphin_rules.md`
