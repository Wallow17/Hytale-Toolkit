#!/usr/bin/env bash
# Pack the per-channel LanceDB outputs into tarballs and emit a manifest.
#
# Inputs (in $REPO_ROOT/hytale-rag/data/{provider}/{channel}/lancedb):
#   data/voyage/release/lancedb/...
#   data/voyage/prerelease/lancedb/...
#
# Outputs (in $OUT_DIR):
#   lancedb-voyage-release.tar.gz
#   lancedb-voyage-prerelease.tar.gz
#   manifest.json
#
# Usage:
#   PROVIDER=voyage RELEASE_VERSION=2026.05.01-43e16373b46 \
#       PRERELEASE_VERSION=2026.05.01-1538e09ba69 \
#       scripts/pack-release.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROVIDER="${PROVIDER:-voyage}"
DATA_ROOT="$REPO_ROOT/hytale-rag/data/$PROVIDER"
OUT_DIR="${OUT_DIR:-$REPO_ROOT/dist/db}"
RELEASE_VERSION="${RELEASE_VERSION:?must set RELEASE_VERSION (e.g. 2026.05.01-XXX)}"
PRERELEASE_VERSION="${PRERELEASE_VERSION:?must set PRERELEASE_VERSION}"

mkdir -p "$OUT_DIR"

for channel in release prerelease; do
    src="$DATA_ROOT/$channel/lancedb"
    if [ ! -d "$src" ]; then
        echo "ERROR: $src not found. Run ingestion for channel '$channel' first." >&2
        exit 1
    fi
    out="$OUT_DIR/lancedb-$PROVIDER-$channel.tar.gz"
    echo "==> packing $channel -> $out"
    # Tar with the lancedb dir as the only top-level entry so extraction
    # reproduces data/{provider}/{channel}/lancedb when extracted into
    # data/{provider}/{channel}/.
    tar -C "$DATA_ROOT/$channel" -czf "$out" lancedb
    ls -lh "$out"
done

cat > "$OUT_DIR/manifest.json" <<EOF
{
  "schema_version": 2,
  "default_channel": "release",
  "channels": {
    "release": {
      "latest": "$RELEASE_VERSION",
      "versions": ["$RELEASE_VERSION"]
    },
    "prerelease": {
      "latest": "$PRERELEASE_VERSION",
      "versions": ["$PRERELEASE_VERSION"]
    }
  }
}
EOF

echo "==> manifest.json"
cat "$OUT_DIR/manifest.json"
echo ""
echo "Done. Artifacts in $OUT_DIR/"
ls -lh "$OUT_DIR"
