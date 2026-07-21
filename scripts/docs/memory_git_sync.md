# 双 Mac 记忆同步（Git，推荐）

IP 会变时，**不要用局域网 rsync**，改用私有 Git 仓库。

## 同步内容

目录：`~/.dc-platform/memory/`  
命令：`bash ~/.dc-platform/scripts/sync-memory-git.sh`

不同步：agent-bus state、tgbot `.env`、VPN、Cursor transcript。

## 一次性：建私有空仓

在公司 Git（与 `dc-parent` 同机）建一个**私有**空项目，例如：

- 建议名：`dmp/dc-youchu-memory`（或你个人命名空间下的 `youchu-memory`）
- 可见性：**Private**（仅自己 / 需要协作的账号）
- **不要**放进 `dc-parent`，避免污染业务仓

记下 SSH 地址，形如：

```text
git@github.com:youchu888/youchu-memory.git
```

## 新 Mac（本机，已有记忆文件）

本机已 `git init` 并做好首次提交的话，只需：

```bash
cd ~/.dc-platform/memory
git remote add origin 'git@github.com:youchu888/youchu-memory.git'
git push -u origin main
```

日常（手动）：

```bash
bash ~/.dc-platform/scripts/sync-memory-git.sh
# 或带说明：
bash ~/.dc-platform/scripts/sync-memory-git.sh "docs: 停留分档交接"
```

## 定时自动同步（两台各装一份）

launchd 每 10 分钟跑一次 `sync-memory-git.sh`（先 pull --rebase 再 push，双机互相协调）：

```bash
bash ~/.dc-platform/scripts/install-memory-git-sync-launchd.sh
# 自定义间隔（秒）：
INTERVAL_SEC=300 bash ~/.dc-platform/scripts/install-memory-git-sync-launchd.sh
# 卸载：
bash ~/.dc-platform/scripts/uninstall-memory-git-sync-launchd.sh
```

日志：`~/.dc-platform/logs/memory-git-sync.log`。  
脚本带并发锁，手动与定时同时触发不会打架；冲突时会 abort 本次 rebase 并在日志提示手动解决。

## 旧 Mac（第一次）

若旧机已有 `~/.dc-platform/memory` 且无 git：

```bash
# 1) 备份
mv ~/.dc-platform/memory ~/.dc-platform/memory.bak.$(date +%Y%m%d)

# 2) 克隆共享库
git clone 'git@github.com:youchu888/youchu-memory.git' ~/.dc-platform/memory

# 3) 把旧机独有、仓库里没有的文件拷回来（可选）
# rsync -a --ignore-existing ~/.dc-platform/memory.bak.*/ ~/.dc-platform/memory/
# 然后在旧机再跑一次 sync-memory-git.sh 推上去
```

日常同样：

```bash
bash ~/.dc-platform/scripts/sync-memory-git.sh
```

（旧机需有 `~/.dc-platform/scripts/sync-memory-git.sh`；可从新机拷贝整个 `~/.dc-platform/scripts/`。）

## 冲突怎么处理

脚本使用 `git pull --rebase --autostash`。  
若两边改了同一文件，rebase 停下时：

```bash
cd ~/.dc-platform/memory
# 编辑冲突文件 → git add → git rebase --continue → git push
```

习惯：**lesson 追加新文件**，少改同一大文件的同一段，冲突会少很多。

## 与局域网 rsync 的关系

`sync-memory-peer.sh` 仍保留作备用；**默认请用本 Git 方案**。
