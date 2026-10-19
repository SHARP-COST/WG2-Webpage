#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_REPO="${1:-$ROOT/../WG2-Hadron-Spectroscopy}"
SOURCE_REF="${2:-main}"

TMP_DIR="$(mktemp -d /tmp/wg2-source-sandbox-XXXXXX)"
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

if [[ -d "$SOURCE_REPO/.git" ]]; then
  SOURCE_REPO_ABS="$(cd "$SOURCE_REPO" && pwd)"
  CLONE_FROM="file://$SOURCE_REPO_ABS"
else
  CLONE_FROM="$SOURCE_REPO"
fi

echo "Cloning source into sandbox: $TMP_DIR"
git clone --depth 1 --branch "$SOURCE_REF" "$CLONE_FROM" "$TMP_DIR/source"
SOURCE_COMMIT="$(git -C "$TMP_DIR/source" rev-parse HEAD)"
echo "Using source commit: $SOURCE_COMMIT"

python3 "$ROOT/scripts/sync_members.py" "$TMP_DIR/source/WG2.list"
python3 "$ROOT/scripts/build_site.py"
python3 "$ROOT/scripts/check_health.py"

echo "Public snapshot checksum:"
shasum -a 256 "$ROOT/data/members.yaml"
