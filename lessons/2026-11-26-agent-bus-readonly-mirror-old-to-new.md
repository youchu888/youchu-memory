# agent-bus 只读镜像（old→new）

tags: agent-bus, dual-mac, readonly-mirror, new-mac

人常在 new-mac、收单权威在 old-mac 时：不迁主、不双开 poller。权威机把 inbox/sent/processed 导出到 `mirrors/agent-bus/from-<host>/`，经 memory-git-sync 到新机，物化到 `~/Library/Application Support/youchu-agent-bus/readonly-mirror/`，只读对照派单。结案时 `agent_bus_send` reply 会 best-effort 再 export 一次。查：`agent-bus-readonly-status.sh`。
