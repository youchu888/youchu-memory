# old-mac / new-mac：安装测试集群 SSH

私钥在仓内是 **AES 加密**（`id_ed25519.enc`），口令与 `bootstrap/git-ssh` **共用**。

## 一次性（old-mac）

1. 确认口令文件已在（与 git-ssh 同一份，不进 git）：
   `cat ~/.dc-platform/config/git-ssh-bundle.pass`
   若没有，从 new-mac 把该文件拷过来（AirDrop / 手动），`chmod 600`。
2. pull 记忆仓后执行：

```bash
cd ~/.dc-platform/memory && git pull --rebase
export GIT_SSH_BUNDLE_PASS="$(cat ~/.dc-platform/config/git-ssh-bundle.pass)"
bash bootstrap/testcluster-ssh/install-on-host.sh
```

3. 连上办公 VPN 后验证：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=10 dolphinscheduler-2 'hostname; whoami'
# 期望：dolphinscheduler-2 / bigdata-dev
ssh dolphinscheduler-2 'sudo -iu hadoop hostname'
```

公钥指纹应是：`SHA256:UrDVEhFOpbfqennSgUjOXxldbCkXmVItaaM+yDwYpBs`（bigdata-dev@dolphinscheduler-2）

## 连接摘要

| 项 | 值 |
|---|---|
| 机器 | dolphinscheduler-2 |
| 外网 | 43.213.29.105（先 VPN，22 只对 VPN） |
| 内网 | 172.31.18.166 |
| 账号 | bigdata-dev（仅私钥，无密码） |
| 本机私钥 | `~/.ssh/id_ed25519_testcluster` |
| 快捷 | `ssh dolphinscheduler-2` |
| 切 hadoop | `sudo -iu hadoop` / `sudo su - hadoop` |

禁止：直连生产 hadoop-1；明文私钥勿提交记忆仓。
