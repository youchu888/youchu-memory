# 工作流水 · 双 Mac 统一汇总

> **权威目录**：`~/.dc-platform/memory/work-log/`（随 `youchu-memory` Git 双机同步）  
> **本机习惯路径**：`CHcode/.cursor/work-log/`（收尾仍写这里，由脚本导出到本目录）

## 目录

```
work-log/
├── README.md                 # 本文件
├── hosts/
│   └── <hostname>/           # 每台 Mac 各自流水（勿互相覆盖）
│       ├── YYYY-MM-DD.md
│       └── reports/YYYY-MM-DD-日报.md
├── YYYY-MM-DD.md             # 【合并稿】各 host 拼在一起（写日报必读）
└── reports/
    └── YYYY-MM-DD-日报.md    # 【正式日报】双机统一后只保留这一份
```

## 日常流程

1. **干活收尾**（任一台）：append  
   `CHcode/.cursor/work-log/YYYY-MM-DD.md`
2. **要出日报 / 定时同步前**：
   ```bash
   python3 ~/.dc-platform/memory/scripts/worklog_dual_mac_sync.py
   bash ~/.dc-platform/scripts/sync-memory-git.sh
   ```
3. **写日报**：先读 `work-log/YYYY-MM-DD.md`（合并稿）+ 各 `hosts/*/…`，再写正式稿；脚本会把正式稿同步到 `work-log/reports/` 并镜像回本地。

## 主机名

默认用 `hostname -s`。若两台撞名，在 `~/.dc-platform/memory/.env.host` 或 shell 里设：

```bash
export WORKLOG_HOST_ID=new-mac   # 或 old-mac
```

建议：
- 新 Mac（编码机）→ `new-mac`（只贡献流水）
- 旧 Mac（bot 机）→ `old-mac`（**正式日报权威**）

正式日报以文件 `work-log/AUTHORITY_HOST` 为准（当前：`old-mac`）。

## 正式日报权威（主人 2026-07-22）

**以旧 Mac（`old-mac`）为准。**

| 机器 | host id | 权限 |
|------|---------|------|
| 旧 Mac（bot 常驻） | `old-mac` | 可覆盖 `work-log/reports/` 正式日报 |
| 新 Mac（编码） | `new-mac` | 只贡献 `hosts/new-mac/` 流水；**不得**覆盖正式日报 |

写日报 / 21:30 自动出报：优先在**旧 Mac**生成正式稿；新 Mac 先把任务写进本机 work-log 并 sync，旧机合并后再定稿。
