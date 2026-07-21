# 工作狂人 · 又初每日学习知识库

> 维护人：又初 · 来源：worker_ant（agent-bus / 群旁听 / dc-platform 文档）

## 目的

每天下班后用 agent-bus 向工作狂人请教，把回复 + 平台文档 + 当日派单经验**结构化沉淀**，供下次开工注入上下文。

## 每日流程（19:30 Asia/Shanghai）

1. **提问**（agent-bus `send_message` → `worker_ant`）  
   模板见 `DAILY_PROMPT.md`
2. **收回复** → 写入 `sessions/YYYY-MM-DD.md`
3. **提炼** → 新规则写 `lessons/YYYY-MM-DD-worker-ant-*.md`（单条一事）
4. **更新索引** → `INDEX.md` 表格 + `MEMORY.md` hook 行
5. **可选** → 拉 dc-platform 文档增量（`platform/docs` API）

## 目录

| 路径 | 作用 |
|------|------|
| `INDEX.md` | 总索引：主题 → lesson / 文档 slug / 会话 |
| `DAILY_PROMPT.md` | 每日提问模板（全量/增量） |
| `context-bootstrap.md` | Agent 冷启动注入摘要（自动生成或手更） |
| `sessions/` | 按日原始问答流水 |
| `../lessons/20260626-worker-ant-collab-cheatsheet.md` | 协作速查 v1（canonical） |

## 工具

```bash
# 问工作狂人
python3 -c "import sys; sys.path.insert(0,'omdb/tgbot'); from agent_bus_client import send_message; print(send_message('...'))"

# 列平台文档
curl -s http://54.255.236.159:8012/api/v1/platform/docs

# 读文档正文（需 token）
curl -s -H "Authorization: Bearer $DCP_TOKEN" \
  http://54.255.236.159:8012/api/v1/platform/docs/raw/{slug}
```

## 关联

- agent-bus 指南：`omdb/tgbot/docs/AGENT互通对接指南.md`
- 自动群学习：`omdb/tgbot/worker_ant_learner.py`
- TG 提醒：`[REMIND: YYYY-MM-DD 19:30 向工作狂人学习并沉淀]`
