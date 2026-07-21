---
date: 2026-07-02
tags: [agent-bus, tg, worker_ant, feedback, prod, attribution, self-evolve]
severity: high
domain: ops
---

# agent-bus TG 镜像三坑 + 反套娃修 bug 纪律

## 背景

bus#836 prod 归因 result 29 列事故：又初无 prod 海豚写权限，应走平台 `request-publish` 让 admin/狂人审。修复过程中出现「修了 A 出 B」：误标 bus 结案、TG 没推到主人、自查告警套娃。

## 坑 / 错误做法

1. **bus 误结案**：403 受阻仍 `reply`+`done` bus#836，后续 `progress` 被镜像当「已结案」过滤 → 主人 TG 看不到平台申请跟进。
2. **`--no-dedup` 不写 TG**：`agent_bus_send.py` 仅在 `dedup=True` 时调 `_mirror_outbound_tg` → 补发消息 bus 有、TG 无。
3. **镜像过度过滤**：`is_closed` 时一律拦 `progress`，连带 `outbound_id` 的出站 progress 也丢。
4. **修 prod 修错目标**：legacy prod（18.141…）发 SQL 当「已修」，active 失败在 **prod_primary**（171982… / task 174729603403591）。
5. **只口头通知主人**：发现 bug 只 TG 解释，不写 lesson → 下次同类修复再踩。

## 正确做法

### 出站 / 镜像

- `agent_bus_send.py`：**只要 API ok 就 mirror**；`dedup` 只控制 `mark_sent` 去重，不控制镜像。
- `agent_bus_tg_mirror.py`：已结案仅拦 `wake`/`ack`；**带 `outbound_id` 的 progress/reply 仍推 TG**。
- **未真正 unblock 禁止 `kind=reply` 结案**（prod 发布 pending / 403 / 只改 legacy 都不算完）。用 `kind=progress` 或 reply 但不 done，直到狂人/admin 确认 prod_primary 版号+补数。

### prod 归因 result 事故

| 项 | 值 |
|---|---|
| prod_primary | proj `171982119739200`, wf `174729604091712`, task `174729603403591` |
| 无 prod 权限 | 更新 `dev-20260610-904` → `request-publish`(reviewer=admin)，**不**直连 publish / legacy 海豚 |
| 脚本 | `dc-platform-server/scripts/request_prod_result_publish_904.py` |

### 反套娃（改 bot/ bus 前必做）

1. **列影响面**：改 A 会不会让 B 失效？（例：关 restart ↔ daemon 托管；关 progress ↔ 主人看不见进展）
2. **一条 diff 一个意图**：TG 镜像 / 自查 / 结案 / prod 发布分开 commit，不混在一轮「顺手修」。
3. **改完必验**：`tail youchu_ai_tg_status.jsonl` + 日志 `sendMessage` + `agent-bus-mirror reply → TG`。
4. **主人指令有误区要讨论**：例「关 TG 推送」vs「修误报根因」——取不误伤可见性的方案。

## 验证

```bash
# 出站 + 镜像
python3 .claude/database/scripts/notify/agent_bus_send.py --to worker_ant --kind progress \
  --reply-to-bus-id N --no-dedup --text "测试镜像"
tail -1 "$HOME/Library/Application Support/youchu-agent-bus/state/youchu_ai_tg_status.jsonl"
rg "sendMessage|mirror.*→ TG" /tmp/tgbot-dc.log | tail -3

# 平台 pending
curl -s -H "Authorization: Bearer $(jq -r .token .claude/database/dc-platform.json)" \
  "http://54.255.236.159:8012/api/v1/dev-sessions/dev-20260610-904/full" | jq '.state_json.target'
```

## 结案标识（bus 回执必带）

任务收尾 reply 正文**必须**含可检索标签，便于主人/TG/狂人一眼看懂状态：

```
[CLOSED·bus#N·又初回执]
【总标识】INCIDENT=RESOLVED | 又初侧=FOLLOW_ONLY
【分项】PROD_SQL=PUBLISHED_29COL | BACKFILL_07-01=SUCCESS | GIT=dev/6805644 ALIGNED
```

本地同步写：
- `.claude/dolphin/wf_cross_env_map.yaml` 顶部 `【结案标识·bus#…】` 注释块
- lesson 本条「变更记录」一行

**禁止**：口头说「处理完了」却无 bus reply:bus:N + done + 标识。

## 变更记录

- 2026-07-02 bus#853/#855：归因 prod 事故狂人 admin 收尾；又初 reply 带 CLOSED 标识；wf_map 写结案块

## 关联

- 代码：`omdb/tgbot/agent_bus_tg_mirror.py`, `omdb/tgbot/bot_health.py`, `.claude/database/scripts/notify/agent_bus_send.py`
- 对照：`.claude/dolphin/wf_cross_env_map.yaml`
- 规则：`.cursor/rules/agent-bus-session.mdc`, `.cursor/skills/self-evolve/SKILL.md`
- 相关 lesson：`2026-07-01-agent-bus-progress-ide-heartbeat.md`, `2026-07-02-dolphin-prod-test-wf-name-map.md`
