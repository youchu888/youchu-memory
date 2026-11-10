#!/usr/bin/env bash
# 本机安装测试集群 dolphinscheduler-2 SSH 钥 + Host 别名
# 私钥仓内为 AES 加密件；口令与 git-ssh 共用 ~/.dc-platform/config/git-ssh-bundle.pass
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
SSH_DIR="${HOME}/.ssh"
KEY_NAME="id_ed25519_testcluster"
mkdir -p "$SSH_DIR"
chmod 700 "$SSH_DIR"

PASS="${GIT_SSH_BUNDLE_PASS:-}"
if [[ -z "$PASS" && -f "$HOME/.dc-platform/config/git-ssh-bundle.pass" ]]; then
  PASS="$(tr -d '\n' < "$HOME/.dc-platform/config/git-ssh-bundle.pass")"
fi
if [[ -z "$PASS" ]]; then
  echo "ERROR: 设置 GIT_SSH_BUNDLE_PASS 或写入 ~/.dc-platform/config/git-ssh-bundle.pass" >&2
  exit 1
fi
if [[ ! -f "$SRC/id_ed25519.enc" ]]; then
  echo "ERROR: 缺少 $SRC/id_ed25519.enc" >&2
  exit 1
fi

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT
if ! openssl enc -d -aes-256-cbc -pbkdf2 -pass "pass:$PASS" -in "$SRC/id_ed25519.enc" -out "$tmp" 2>/dev/null; then
  echo "ERROR: 解密失败（口令不对或文件损坏）" >&2
  exit 1
fi

DEST="$SSH_DIR/$KEY_NAME"
if [[ -f "$DEST" ]] && ! cmp -s "$tmp" "$DEST"; then
  bak="$DEST.bak.$(date +%Y%m%d%H%M%S)"
  cp -f "$DEST" "$bak"
  [[ -f "$DEST.pub" ]] && cp -f "$DEST.pub" "${bak}.pub"
  echo "info: 已有不同私钥，备份到 $bak"
fi

umask 077
cp -f "$tmp" "$DEST"
chmod 600 "$DEST"
if [[ -f "$SRC/id_ed25519.pub" ]]; then
  cp -f "$SRC/id_ed25519.pub" "$DEST.pub"
  chmod 644 "$DEST.pub"
fi

if [[ -f "$SRC/known_hosts.testcluster" ]]; then
  touch "$SSH_DIR/known_hosts"
  chmod 600 "$SSH_DIR/known_hosts"
  while IFS= read -r line; do
    [[ -z "$line" || "$line" == \#* ]] && continue
    host="${line%% *}"
    if ! grep -q "^${host} " "$SSH_DIR/known_hosts" 2>/dev/null \
      && ! grep -q "^\\[${host}\\]" "$SSH_DIR/known_hosts" 2>/dev/null; then
      echo "$line" >> "$SSH_DIR/known_hosts"
    fi
  done < "$SRC/known_hosts.testcluster"
fi

CFG="$SSH_DIR/config"
touch "$CFG"
chmod 600 "$CFG"
if ! grep -qE '^Host[[:space:]]+dolphinscheduler-2([[:space:]]|$)' "$CFG" 2>/dev/null; then
  {
    echo ""
    echo "Host dolphinscheduler-2 ds2-test"
    echo "  HostName 43.213.29.105"
    echo "  User bigdata-dev"
    echo "  IdentityFile ~/.ssh/${KEY_NAME}"
    echo "  IdentitiesOnly yes"
  } >> "$CFG"
  echo "info: 已写入 Host dolphinscheduler-2"
else
  echo "info: Host dolphinscheduler-2 已存在，未改 config"
fi

echo "OK 已安装 ~/.ssh/${KEY_NAME}"
ssh-keygen -lf "$DEST.pub" 2>/dev/null || true
echo "用法: 先连办公 VPN，再 ssh dolphinscheduler-2"
echo "切 hadoop: sudo -iu hadoop"
