# old-mac：安装 git SSH 钥

私钥在仓内是 **AES 加密**（`id_ed25519.enc`），避免 GitHub push protection 拦明文。

## 一次性

1. 在 **new-mac** 看口令文件（不进 git）：
   `cat ~/.dc-platform/config/git-ssh-bundle.pass`
2. 把口令带到 old-mac（AirDrop / 手动），写入：
   `mkdir -p ~/.dc-platform/config && echo '口令' > ~/.dc-platform/config/git-ssh-bundle.pass && chmod 600 ~/.dc-platform/config/git-ssh-bundle.pass`
3. pull 记忆仓后执行：

```bash
cd ~/.dc-platform/memory && git pull --rebase
export GIT_SSH_BUNDLE_PASS="$(cat ~/.dc-platform/config/git-ssh-bundle.pass)"
bash bootstrap/git-ssh/install-on-host.sh
ssh -T git@github.com
```

公钥指纹应是：`SHA256:lunkm/WTZMbSm0OjjixZN8KApqY5RJ5Xp2mG9ZGMQbg`（DN6517@jsyyds.com）
