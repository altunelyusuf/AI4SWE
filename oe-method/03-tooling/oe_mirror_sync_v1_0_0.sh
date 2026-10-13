#!/usr/bin/env bash
# oe_mirror_sync_v1_0_0.sh — keep the standalone oe-method mirror in step with the monorepo.
#
# Owner direction (2026-09-24): oe-pack stays private as the development source that carries the
# history; links point to oe-method; the standalone oe-method repository stays alive, private and
# shared by invitation. It is a MIRROR of the monorepo's oe-method/ folder -- never edited on its
# own -- so it must be updated whenever the monorepo copy changes, or a visible notice must say an
# update is needed.
#
# Usage:
#   bash oe_mirror_sync_v1_0_0.sh <token>            sync the mirror (verify, commit, push)
#   bash oe_mirror_sync_v1_0_0.sh <token> --check    report only: IN SYNC (exit 0) / STALE (exit 3)
#
# Environment (defaults in brackets):
#   OE_SOURCE_REPO [your-account/Ontologies]   OE_MIRROR_REPO [your-account/oe-method]
#   OE_MIRROR_PATH [oe-method]                 OE_GIT_NAME / OE_GIT_EMAIL for the mirror commit
#
# Exit codes: 0 in sync or synced; 3 stale (--check only); 4 sync attempted but failed -- the
# mirror is NOT updated and a human must act (the caller is expected to raise a notice).
#
# Guarantees: the copied tree is verified against the package's own manifest (listed files intact,
# no stowaways) before anything is committed; the mirror's own history is kept (a new commit on
# top, never a force-push); MIRROR.md is the only mirror-only file, and it states the source
# repository, path, commit and version the mirror was taken from.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOKEN="${1:?usage: oe_mirror_sync_v1_0_0.sh <token> [--check]}"
MODE="${2:-sync}"
SRC_REPO="${OE_SOURCE_REPO:-your-account/Ontologies}"
MIR_REPO="${OE_MIRROR_REPO:-your-account/oe-method}"
PKG="${OE_MIRROR_PATH:-oe-method}"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
fail() { echo "MIRROR NOTICE: $* -- the mirror $MIR_REPO is NOT up to date; a manual update is needed." >&2; exit 4; }

git clone -q --depth 1 "https://x-access-token:${TOKEN}@github.com/${SRC_REPO}.git" "$TMP/src" || fail "cannot clone $SRC_REPO"
git clone -q "https://x-access-token:${TOKEN}@github.com/${MIR_REPO}.git" "$TMP/mir" || fail "cannot clone $MIR_REPO"
[ -f "$TMP/src/$PKG/VERSION.txt" ] || fail "no $PKG/VERSION.txt in $SRC_REPO"
SRC_VER=$(tr -d ' \n\r' < "$TMP/src/$PKG/VERSION.txt")
SRC_SHA=$(git -C "$TMP/src" rev-parse --short HEAD)
MIR_VER=$(tr -d ' \n\r' < "$TMP/mir/VERSION.txt" 2>/dev/null || echo "none")

if [ "$MODE" = "--check" ]; then
  if [ "$SRC_VER" = "$MIR_VER" ]; then echo "mirror IN SYNC: $MIR_REPO at v$MIR_VER"; exit 0; fi
  echo "mirror STALE: $MIR_REPO at v$MIR_VER, $SRC_REPO/$PKG at v$SRC_VER -- update needed"; exit 3
fi

if [ "$SRC_VER" = "$MIR_VER" ]; then echo "mirror already in sync at v$SRC_VER -- nothing to do"; exit 0; fi

# replace the mirror's tree with the package (keep only .git), then add the mirror notice
find "$TMP/mir" -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
cp -a "$TMP/src/$PKG/." "$TMP/mir/"
find "$TMP/mir" -name __pycache__ -type d -prune -exec rm -rf {} + 2>/dev/null || true

MF=$(cd "$TMP/mir" && ls MANIFEST_SHA256*.txt 2>/dev/null | sort -V | tail -1) || true
[ -n "${MF:-}" ] || fail "no manifest in the copied package"
( cd "$TMP/mir" && python3 "$HERE/verify_manifest_v1_1_0.py" "$MF" --root . --exclude PUBLISH_RECORD.ttl --exclude MIRROR.md >/tmp/mirror_verify.$$ 2>&1 ) || {
  # the only tolerated mismatch is the publish record, rewritten by the publisher after the manifest
  grep -q "MISMATCH (1)" /tmp/mirror_verify.$$ && grep -q "^    PUBLISH_RECORD.ttl$" /tmp/mirror_verify.$$ \
    && grep -q "stowaways: 0" /tmp/mirror_verify.$$ || { cat /tmp/mirror_verify.$$ >&2; fail "copied tree failed manifest verification"; }
}
rm -f /tmp/mirror_verify.$$

cat > "$TMP/mir/MIRROR.md" <<EOF
# This repository is a mirror

It carries the \`${PKG}\` package exactly as published in the monorepo \`${SRC_REPO}\`, folder
\`${PKG}/\`. Do not edit it here: changes are made in the monorepo and mirrored.

| | |
|---|---|
| Source | \`${SRC_REPO}\`, folder \`${PKG}/\` |
| Source commit | \`${SRC_SHA}\` |
| Package version | v${SRC_VER} |
| Mirrored | $(date -u +%Y-%m-%dT%H:%M:%SZ) |

This file is the only one that exists here and not in the source.
EOF

cd "$TMP/mir"
git config user.name "${OE_GIT_NAME:-OEE governance session}"
git config user.email "${OE_GIT_EMAIL:-oee@example.org}"
git add -A
git commit -q -m "mirror: ${PKG} v${SRC_VER} from ${SRC_REPO}@${SRC_SHA}" -m "Previous mirror version: v${MIR_VER}. Tree verified against the package's own manifest before commit." || fail "nothing to commit"
git push -q origin HEAD 2>/dev/null || fail "push to $MIR_REPO rejected"
echo "mirror updated: $MIR_REPO v${MIR_VER} -> v${SRC_VER} (commit $(git rev-parse --short HEAD))"
