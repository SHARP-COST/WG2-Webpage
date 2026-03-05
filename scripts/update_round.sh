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

WG2_SOURCE_MEMBERS="$TMP_DIR/source/members" python3 "$ROOT/scripts/build_site.py"

echo "Output checksums:"
shasum -a 256 \
  "$ROOT/data/members.yaml" \
  "$ROOT/data/members.json" \
  "$ROOT/site/data/members.yaml" \
  "$ROOT/site/data/members.json"
