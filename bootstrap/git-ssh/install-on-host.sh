#!/usr/bin/env bash
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
SSH_DIR="${HOME}/.ssh"
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

if [[ -f "$SSH_DIR/id_ed25519" ]] && ! cmp -s "$tmp" "$SSH_DIR/id_ed25519"; then
  bak="$SSH_DIR/id_ed25519.bak.$(date +%Y%m%d%H%M%S)"
  cp -f "$SSH_DIR/id_ed25519" "$bak"
  [[ -f "$SSH_DIR/id_ed25519.pub" ]] && cp -f "$SSH_DIR/id_ed25519.pub" "${bak}.pub"
  echo "info: 已有不同私钥，备份到 $bak"
fi

umask 077
cp -f "$tmp" "$SSH_DIR/id_ed25519"
chmod 600 "$SSH_DIR/id_ed25519"
if [[ -f "$SRC/id_ed25519.pub" ]]; then
  cp -f "$SRC/id_ed25519.pub" "$SSH_DIR/id_ed25519.pub"
  chmod 644 "$SSH_DIR/id_ed25519.pub"
fi

if [[ -f "$SRC/known_hosts.github" ]]; then
  touch "$SSH_DIR/known_hosts"
  chmod 600 "$SSH_DIR/known_hosts"
  while IFS= read -r line; do
    [[ -z "$line" || "$line" == \#* ]] && continue
    host="${line%% *}"
    if ! grep -q "^${host} " "$SSH_DIR/known_hosts" 2>/dev/null; then
      echo "$line" >> "$SSH_DIR/known_hosts"
    fi
  done < "$SRC/known_hosts.github"
fi

CFG="$SSH_DIR/config"
if [[ ! -f "$CFG" ]] || ! grep -q 'Host github.com' "$CFG" 2>/dev/null; then
  {
    echo ""
    echo "Host github.com"
    echo "  HostName github.com"
    echo "  User git"
    echo "  IdentityFile ~/.ssh/id_ed25519"
    echo "  IdentitiesOnly yes"
  } >> "$CFG"
  chmod 600 "$CFG"
fi

# shellcheck disable=SC1091
[[ -f "$SRC/remotes.env" ]] && source "$SRC/remotes.env" && echo "MEMORY_GIT_REMOTE=${MEMORY_GIT_REMOTE:-}"

echo "OK 已安装 ~/.ssh/id_ed25519"
ssh-keygen -lf "$SSH_DIR/id_ed25519.pub" 2>/dev/null || true
echo "下一步: ssh -T git@github.com"
