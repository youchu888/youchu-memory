# 红线续篇 · bus 正文禁前缀

39. **给 worker_ant 发 bus：正文禁任何前缀标签，payload.kind 禁 reply/ack** — 勿写 `[REPLY]`/`[ACK]`/`[重发确认]`；用 `--kind progress` 直写正文，成功后本地 mark_processed。见 lesson `2026-11-18-butler收件静默丢弃REPLY-ACK前缀-bus13925.md`（bus#13925/#13933）。
