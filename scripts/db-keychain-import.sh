#!/usr/bin/env bash
# 将数据库密码写入 Keychain（不回显、不写进可同步文件）
# 用法:
#   bash db-keychain-import.sh              # 交互导入 test+prod
#   bash db-keychain-import.sh --from-cnf   # 从旧 my.cnf 迁移后提示删除明文
#   bash db-keychain-import.sh test|prod    # 只导一个 profile
set -euo pipefail

ROOT="${DC_PLATFORM_ROOT:-$HOME/.dc-platform}"
HOSTS="${DC_DB_HOSTS:-$ROOT/config/db.hosts.conf}"
EXAMPLE="$ROOT/config/db.hosts.example"
OLD_TEST="${DC_OLD_CNF_TEST:-$HOME/Desktop/CHcode/.claude/database/my.cnf.test}"
OLD_PROD="${DC_OLD_CNF_PROD:-$HOME/Desktop/CHcode/.claude/database/my.cnf.prod}"

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

_cnf_get() {
  local file="$1" key="$2"
  awk -F= -v k="$key" '
    $0 ~ "^" k "=" {
      sub("^[^=]+=", "", $0)
      gsub(/\r/, "", $0)
      gsub(/^"/, "", $0); gsub(/"$/, "", $0)
      gsub(/^'\''/, "", $0); gsub(/'\''$/, "", $0)
      print $0
      exit
    }
  ' "$file"
}

_ensure_hosts() {
  if [[ ! -f "$HOSTS" ]]; then
    if [[ -f "$EXAMPLE" ]]; then
      cp "$EXAMPLE" "$HOSTS"
      chmod 600 "$HOSTS"
      echo "已创建 $HOSTS (请核对 host/user)"
    else
      echo "缺少 $EXAMPLE" >&2
      exit 1
    fi
  fi
}

_set_kc() {
  local service="$1" account="$2" pass="$3"
  # -U 已存在则更新
  security add-generic-password -U -s "$service" -a "$account" -w "$pass" >/dev/null
  echo "Keychain OK service=$service account=$account"
}

_import_interactive() {
  local profile="$1"
  local service user
  service="$(_read_section "$profile" service "$HOSTS")"
  user="$(_read_section "$profile" user "$HOSTS")"
  if [[ -z "$service" || -z "$user" ]]; then
    echo "[$profile] hosts 缺 service/user" >&2
    exit 1
  fi
  local pass
  echo -n "[$profile] 输入密码（不回显）: "
  read -r -s pass
  echo
  if [[ -z "$pass" ]]; then
    echo "空密码，跳过 $profile" >&2
    return 0
  fi
  _set_kc "$service" "$user" "$pass"
}

_import_from_cnf() {
  local profile="$1" cnf="$2"
  if [[ ! -f "$cnf" ]]; then
    echo "无文件 $cnf，跳过 $profile" >&2
    return 0
  fi
  local host port user database pass service
  host="$(_cnf_get "$cnf" host)"
  port="$(_cnf_get "$cnf" port)"
  user="$(_cnf_get "$cnf" user)"
  database="$(_cnf_get "$cnf" database)"
  pass="$(_cnf_get "$cnf" password)"
  if [[ -z "$pass" || -z "$user" ]]; then
    echo "[$profile] $cnf 无 password/user，跳过" >&2
    return 0
  fi

  _ensure_hosts
  # 用 cnf 非密字段覆盖 hosts（保留 service 名）
  service="$(_read_section "$profile" service "$HOSTS")"
  if [[ -z "$service" ]]; then
    if [[ "$profile" == test ]]; then service=youchu.sr.test; else service=youchu.sr.prod; fi
  fi

  python3 - "$HOSTS" "$profile" "$service" "$host" "$port" "$user" "$database" <<'PY'
import sys
path, profile, service, host, port, user, database = sys.argv[1:8]
port = port or "9030"
database = database or "ads"
text = open(path, encoding="utf-8", errors="ignore").read().splitlines()
out = []
i = 0
replaced = False
section = f"[{profile}]"
while i < len(text):
    line = text[i]
    if line.strip() == section:
        out.append(section)
        i += 1
        block = {
            "service": service,
            "host": host,
            "port": port,
            "user": user,
            "database": database,
            "charset": "utf8mb4",
            "protocol": "tcp",
        }
        while i < len(text) and not text[i].strip().startswith("["):
            i += 1
        for k, v in block.items():
            out.append(f"{k}={v}")
        replaced = True
        continue
    out.append(line)
    i += 1
if not replaced:
    out.append("")
    out.append(section)
    out.append(f"service={service}")
    out.append(f"host={host}")
    out.append(f"port={port}")
    out.append(f"user={user}")
    out.append(f"database={database}")
    out.append("charset=utf8mb4")
    out.append("protocol=tcp")
open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
PY
  chmod 600 "$HOSTS"
  _set_kc "$service" "$user" "$pass"
  echo "[$profile] 已从 cnf 导入 Keychain，并更新 hosts 非密字段"
}

MODE=interactive
ONLY=""
for arg in "$@"; do
  case "$arg" in
    --from-cnf) MODE=from-cnf ;;
    test|prod) ONLY="$arg" ;;
    -h|--help)
      sed -n '2,8p' "$0"
      exit 0
      ;;
    *)
      echo "未知参数: $arg" >&2
      exit 1
      ;;
  esac
done

_ensure_hosts

profiles=(test prod)
if [[ -n "$ONLY" ]]; then
  profiles=("$ONLY")
fi

if [[ "$MODE" == from-cnf ]]; then
  for p in "${profiles[@]}"; do
    if [[ "$p" == test ]]; then
      _import_from_cnf test "$OLD_TEST"
    else
      _import_from_cnf prod "$OLD_PROD"
    fi
  done
else
  for p in "${profiles[@]}"; do
    _import_interactive "$p"
  done
fi

echo "下一步: bash $ROOT/scripts/ensure-db-cnf.sh"
