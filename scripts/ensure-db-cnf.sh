#!/usr/bin/env bash
# 从 Keychain + db.hosts.conf 生成 ~/.dc-platform/secrets/my.cnf.{test,prod}（0600）
# 不打印密码。
set -euo pipefail

ROOT="${DC_PLATFORM_ROOT:-$HOME/.dc-platform}"
HOSTS="${DC_DB_HOSTS:-$ROOT/config/db.hosts.conf}"
OUT_DIR="${DC_DB_SECRETS:-$ROOT/secrets}"
EXAMPLE="$ROOT/config/db.hosts.example"

if [[ ! -f "$HOSTS" ]]; then
  echo "缺少 $HOSTS" >&2
  echo "先: cp \"$EXAMPLE\" \"$HOSTS\" 并填写 host/user" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"
chmod 700 "$OUT_DIR"

# 读 section 字段（简单 INI：key=value）
_read_section() {
  local section="$1" key="$2" file="$3"
  awk -v s="[$section]" -v k="$key" '
    $0 == s { in_s=1; next }
    /^\[/ { in_s=0 }
    in_s && $0 ~ "^" k "=" {
      sub("^[^=]+=", "", $0)
      gsub(/\r/, "", $0)
      print $0
      exit
    }
  ' "$file"
}

_gen_one() {
  local profile="$1"
  local service host port user database charset protocol pass out
  service="$(_read_section "$profile" service "$HOSTS")"
  host="$(_read_section "$profile" host "$HOSTS")"
  port="$(_read_section "$profile" port "$HOSTS")"
  user="$(_read_section "$profile" user "$HOSTS")"
  database="$(_read_section "$profile" database "$HOSTS")"
  charset="$(_read_section "$profile" charset "$HOSTS")"
  protocol="$(_read_section "$profile" protocol "$HOSTS")"
  charset="${charset:-utf8mb4}"
  protocol="${protocol:-tcp}"
  port="${port:-9030}"

  if [[ -z "$service" || -z "$host" || -z "$user" ]]; then
    echo "[$profile] 缺少 service/host/user，检查 $HOSTS" >&2
    exit 1
  fi
  if [[ "$host" == YOUR_* ]]; then
    echo "[$profile] host 仍是占位符，请编辑 $HOSTS" >&2
    exit 1
  fi

  if ! pass="$(security find-generic-password -s "$service" -a "$user" -w 2>/dev/null)"; then
    echo "[$profile] Keychain 无项 service=$service account=$user" >&2
    echo "先跑: bash $ROOT/scripts/db-keychain-import.sh" >&2
    exit 1
  fi
  if [[ -z "$pass" ]]; then
    echo "[$profile] Keychain 密码为空" >&2
    exit 1
  fi

  out="$OUT_DIR/my.cnf.$profile"
  umask 077
  cat >"$out" <<EOF
# 由 ensure-db-cnf.sh 生成 — 勿提交、勿同步
# 密源: Keychain service=$service account=$user
[client]
host=$host
port=$port
user=$user
password=$pass
database=$database
default-character-set=$charset
protocol=$protocol
EOF
  chmod 600 "$out"
  echo "OK $out (mode 600, password from Keychain)"
}

_gen_one test
_gen_one prod
echo "ensure-db-cnf: done"
