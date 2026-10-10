# agent-bus 手工迁主

tags: agent-bus, failover, old-mac, new-mac

old-mac 要下线时不必干等。单主，按 runbook 迁到 new-mac：先卸掉 `com.youchu.agent-bus-poller`（KeepAlive，只 kill 会复活），确认没有 poller 进程，再拷 `youchu_ai.offset`、`youchu_ai_processed.json`、`youchu_ai_history_seal_cutoff`，把 `AUTHORITY_HOST` 改成 new-mac 并同步记忆仓，最后才在 new-mac 启 poller。两台不许同时拉。

原文：`runbooks/agent-bus-manual-failover.md`
