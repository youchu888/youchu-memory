---
date: 2026-05-25
tags: [api, dc-platform, dolphin, token]
severity: medium
domain: ops
---

# dc-platform API token（dcp_）≠ 海豚 Scheduler token

## 背景

用平台 API 查血缘、用 `dolphin_ops` 直连海豚调度。

## 坑 / 错误做法

- 把 `dcp_...` 写入 `.claude/dolphinscheduler.json` → 海豚 API **401**。
- 用海豚 token 调 `http://54.255.236.159:8012/api/v1/me` → 无效。

## 正确做法

| 用途 | 配置 | 认证 |
|------|------|------|
| 血缘 / 元数据 / 表详情 | `.claude/database/dc-platform.json` | `Bearer dcp_...` |
| 海豚发布 / 补数 / 查实例 | `.claude/dolphinscheduler.json` | 海豚 UI 生成的 hex token |

非 admin 的 dcp token：`/api/v1/dolphin/projects` 可能返回空列表，但 `/lineage`、`/tables` 仍可用。

## 验证

```bash
curl -s -H "Authorization: Bearer $(jq -r .token .claude/database/dc-platform.json)" \
  http://54.255.236.159:8012/api/v1/me
python3 -m dolphin_ops.cli ping --env prod
```

## 关联

- 文档：`CH/vpn/api-reference.md`
- `CONNECTIONS.md` dc-platform 小节
