# Feedback：work-log 跨 Agent + 双 Mac 共享（日报/周报）

**适用**：又初及所有 Cursor Agent / 子 Agent · **双 Mac 经 youchu-memory 汇总**

## 问题

- 主会话与子 Agent transcript **分离**
- **新 Mac / 旧 Mac** 各写各的日报 → 内容不一致
- `.cursor/work-log/` 不进业务 Git，原先也不进记忆仓

## 约定

### 任务收尾（必做）

写入 **`CHcode/.cursor/work-log/YYYY-MM-DD.md`**（Asia/Shanghai，工作日）。

### 双机同步（必做）

```bash
python3 ~/.dc-platform/memory/scripts/worklog_dual_mac_sync.py
bash ~/.dc-platform/scripts/sync-memory-git.sh
```

导出到 `~/.dc-platform/memory/work-log/hosts/<new-mac|old-mac>/`，合并为 `work-log/YYYY-MM-DD.md`。

本机身份（不进 Git）：

```bash
echo 'export WORKLOG_HOST_ID=new-mac' > ~/.dc-platform/memory/.env.host  # 编码机
echo 'export WORKLOG_HOST_ID=old-mac' > ~/.dc-platform/memory/.env.host  # bot 机
```

### 写日报前（主人 2026-08-01 铁律）

「整理今天日报」**默认多 Agent + 多设备**；**先同步再汇总**，禁止只扫本机会话。

```bash
bash ~/.dc-platform/scripts/prepare_daily_report_sync.sh          # 今日
bash ~/.dc-platform/scripts/prepare_daily_report_sync.sh YYYY-MM-DD
```

1. 脚本跑 `sync-memory-git.sh`（pull + 导出 hosts + merge + push）并打印 new-mac/old-mac 是否有当日流水
2. 读 **`~/.dc-platform/memory/work-log/YYYY-MM-DD.md`**（合并稿）
3. 扫本机 transcript + 狂人派单
4. 正式稿：`work-log/reports/`（memory 权威，old-mac）+ 镜像本地 `.cursor/work-log/reports/`
5. 若某机缺 `hosts/<id>/当日.md`：交稿时必须点明缺机

**跨机前提**：活发生在哪台，就在哪台写 `.cursor/work-log/当日.md`；Cursor transcript **不同步**。

## 禁止

- 不要只根据当前会话写日报
- 不要把 token 写进 work-log
- 不要两台长期各留一份互不同步的正式日报
