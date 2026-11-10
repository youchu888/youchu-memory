# 测试集群 dolphinscheduler-2 SSH

- 机器：dolphinscheduler-2
- 外网：43.213.29.105（先连办公 VPN，22 只对 VPN 开放）
- 内网：172.31.18.166
- 账号：bigdata-dev（私钥认证，无密码）
- 切 hadoop：`sudo su - hadoop` / `sudo -iu hadoop`
- 本机快捷：`ssh dolphinscheduler-2`（~/.ssh/config Host）
- 双机安装包：`bootstrap/testcluster-ssh/`（加密私钥 + `install-on-host.sh`）
  - new-mac 源钥：`/Users/mac/Desktop/CH/id_ed25519`
  - 安装后统一：`~/.ssh/id_ed25519_testcluster`
  - old-mac：`bash bootstrap/testcluster-ssh/install-on-host.sh`（见同目录 INSTALL.md；口令共用 git-ssh-bundle.pass）
- 关联：bus#12984 / #12992（测试环境 Flink + 调度器）
- 更新：2026-11-10 已验通；同日把连接方式同步进记忆仓供 old-mac 安装
