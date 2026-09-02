---
date: 2026-09-02
tags: [my.cnf, vpn, starrocks, datacheck, network]
severity: high
domain: ops
---

# DB 连不上先验网络/VPN，勿先断「密码过期」

## 背景

本机 pymysql 连 prod/test SR 报 1045；MCP 同环境可查。误判为 my.cnf 密码过期，TG 私聊主人；VPN 稳定后同密码本机即通。

## 坑 / 错误做法

- 见 1045 / timeout 就下结论「账号密码过期/用错」
- 未与平台 `/api/v1/db-connections` 或 MCP 同源配置对照
- 未在同一网络状态下复测（VPN 开/关、跳板 vs 本机直连）
- 把 metadata 内网 timeout 与 SR 公网问题混为一谈

## 正确做法

1. **先分层**：TCP 通否 → 同 cred 从平台 API 拉一份对照 → 本机再测
2. **1045 仍可能是网络中间层/路由/VPN 不稳**，须 VPN 稳定后 **立刻复测同一密码**
3. **MCP 能查、本机不能** → 优先查本机 VPN/路由，不是先换密码
4. **`172.31.x` metadata** → 内网，本机通常需跳板；与 SR 公网 9030 分开判断
5. 对外只说「网络/凭证待验」，**确认前不说「密码过期」**

## 验证

```bash
# 平台 canonical（token 从 dc-platform.json）
curl -sS -H "Authorization: Bearer $TOKEN" http://54.255.236.159:8012/api/v1/db-connections

# 本机复测（与 my.cnf 同 cred）
python3 -c "import pymysql; ... SELECT current_user()"
```

两端 OK 才算本机 SR 通路正常。

## 关联

- 协作速查：prod 必 my.cnf.prod；test 稀疏勿当 prod 异常
- lesson：`2026-08-26-tg-sql-queue-test-vs-agent-prod.md`（环境混用）
