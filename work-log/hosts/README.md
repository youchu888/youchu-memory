# 各机流水目录

每台 Mac 一个子目录，由 `worklog_dual_mac_sync.py` 自动写入。

| 建议 id | 机器 |
|---------|------|
| `new-mac` | 编码 / Cursor 主用 |
| `old-mac` | TG bot / agent-bus 常驻 |

设置（本机，不进 Git）：

```bash
echo 'export WORKLOG_HOST_ID=old-mac' > ~/.dc-platform/memory/.env.host
```

然后：

```bash
python3 ~/.dc-platform/memory/scripts/worklog_dual_mac_sync.py
bash ~/.dc-platform/scripts/sync-memory-git.sh
```
