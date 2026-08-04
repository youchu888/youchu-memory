#!/usr/bin/env bash
# 从开发平台拉取最新官方 dc-platform vsix 并装进 Cursor（双 Mac 通用）
# 用法: bash ~/.dc-platform/scripts/install-dc-extension-latest.sh [目标版本，默认 latest]
set -euo pipefail

BASE_URL="${DC_EXTENSION_BASE:-http://54.255.236.159:8012}"
CACHE_DIR="${HOME}/.dc-platform/extension"
CURSOR_BIN="${CURSOR_BIN:-/Applications/Cursor.app/Contents/Resources/app/bin/cursor}"

mkdir -p "${CACHE_DIR}"

if [[ "${1:-}" == "" || "${1}" == "latest" ]]; then
  META="$(curl -fsSL "${BASE_URL}/api/v1/extension/version")"
  VERSION="$(node -e "const m=JSON.parse(process.argv[1]); process.stdout.write(m.version||'');" "${META}")"
  FILENAME="$(node -e "const m=JSON.parse(process.argv[1]); process.stdout.write(m.filename||'');" "${META}")"
  EXPECT_SHA="$(node -e "const m=JSON.parse(process.argv[1]); process.stdout.write(m.sha256||'');" "${META}")"
else
  VERSION="${1}"
  FILENAME="dc-platform-${VERSION}.vsix"
  META="$(curl -fsSL "${BASE_URL}/api/v1/extension/version")"
  EXPECT_SHA="$(node -e "const m=JSON.parse(process.argv[1]); process.stdout.write(m.version==='${VERSION}'?m.sha256:'');" "${META}")"
fi

VSIX="${CACHE_DIR}/${FILENAME}"
URL="${BASE_URL}/api/v1/extension/download/latest"
if [[ "${1:-}" != "" && "${1}" != "latest" ]]; then
  URL="${BASE_URL}/api/v1/extension/download/${FILENAME}"
fi

echo "[install-dc-extension] target=${VERSION} file=${FILENAME}"

if [[ ! -f "${VSIX}" ]] || [[ "$(shasum -a 256 "${VSIX}" | awk '{print $1}')" != "${EXPECT_SHA}" ]]; then
  rm -f "${VSIX}"
  echo "[install-dc-extension] downloading (resume ok)…"
  curl -C - -fsSL -m 600 -o "${VSIX}" "${URL}"
fi

ACTUAL_SHA="$(shasum -a 256 "${VSIX}" | awk '{print $1}')"
if [[ -n "${EXPECT_SHA}" && "${ACTUAL_SHA}" != "${EXPECT_SHA}" ]]; then
  echo "[install-dc-extension] sha256 mismatch: got ${ACTUAL_SHA}, want ${EXPECT_SHA}" >&2
  exit 1
fi

if [[ ! -x "${CURSOR_BIN}" ]]; then
  echo "[install-dc-extension] Cursor CLI not found: ${CURSOR_BIN}" >&2
  exit 1
fi

"${CURSOR_BIN}" --install-extension "${VSIX}" --force
INSTALLED_DIR="$(ls -d "${HOME}/.cursor/extensions/dc-platform.dc-platform-${VERSION}" 2>/dev/null || true)"
if [[ -n "${INSTALLED_DIR}" ]]; then
  echo "[install-dc-extension] ✅ installed $(node -p "require('${INSTALLED_DIR}/package.json').version")"
else
  echo "[install-dc-extension] installed; reload Cursor window to activate"
fi
