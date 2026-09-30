# bootstrap（双机交接）

| 目录 | 用途 |
|------|------|
| `git-ssh/` | youchu-memory SSH 公钥 + **加密**私钥 + old-mac 安装脚本 |

old-mac：先写口令到 `~/.dc-platform/config/git-ssh-bundle.pass`，再跑 `bash bootstrap/git-ssh/install-on-host.sh`（见 `git-ssh/INSTALL.md`）。
