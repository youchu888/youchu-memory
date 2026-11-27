# agent-bus 只读镜像

权威机（`AUTHORITY_HOST`）导出 `from-<host>/`；其它机经 memory-git-sync 拉取后物化到
`~/Library/Application Support/youchu-agent-bus/readonly-mirror/`。

**禁止**在非权威机用这份副本启 poller / 写 processed / 当 inbox 真源。

- last_export_host: `old-mac`
- authority: `old-mac`
- updated: 2026-11-27T08:07:15+0800
