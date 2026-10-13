#!/usr/bin/env bash
# v1.2.0: REPO and the git commit identity were hardcoded, meaning oe-method's own "cleaned,
# distributed" copy shipped the real account name and personal identity to every collaborator.
# Parameterized via OE_TARGET_REPO / OE_GIT_NAME / OE_GIT_EMAIL, matching oe_publish_v1_5_4.sh's
# own fix, for the same reason.
# oe_rehydrate_v1_2_0.sh — restore a governed package from GitHub into a fresh Claude container.
# Usage:  bash repo-tooling/oe_rehydrate_v1_2_0.sh <token> [package]        package defaults to oe-pack
# Satisfies L-85 (container is wiped between sessions) without a zip upload.
set -euo pipefail
TOKEN="${1:?usage: oe_rehydrate_v1_2_0.sh <token> [package]}"
PKG="${2:-oe-pack}"
REPO="${OE_TARGET_REPO:-your-account/Ontologies}"
WORK="/home/claude/Ontologies"

pip install rdflib pyshacl --break-system-packages -q
rm -rf "$WORK"
git clone -q "https://x-access-token:${TOKEN}@github.com/${REPO}.git" "$WORK"
cd "$WORK"
git remote set-url origin "https://github.com/${REPO}.git"
echo "token scrubbed: $(grep -c "x-access-token" .git/config || true) refs in .git/config"
git config user.name "${OE_GIT_NAME:-the method author}"
git config user.email "${OE_GIT_EMAIL:-yusuf@altunel.dev}"

cd "$WORK/$PKG"
echo "== $PKG @ $(cat VERSION.txt 2>/dev/null || echo '?') =="
MF=$(ls MANIFEST_SHA256*.txt 2>/dev/null | sort -V | tail -1)
grep -v '^#' "$MF" | grep . | sed -E 's/[[:space:]]+\([0-9]+b\)[[:space:]]*$//' > /tmp/_mf.txt
OK=$(sha256sum -c /tmp/_mf.txt 2>/dev/null | grep -c ': OK$' || true)
N=$(grep -c . /tmp/_mf.txt)
echo "manifest: $OK/$N"
[ "$OK" = "$N" ] || { echo "MANIFEST MISMATCH — stop and investigate"; exit 1; }

python3 - <<'PY'
import glob, rdflib
fs = glob.glob('**/*.ttl', recursive=True); bad = []; t = 0
for f in fs:
    try:
        g = rdflib.Graph(); g.parse(f); t += len(g)
    except Exception as e:
        bad.append((f, str(e)[:60]))
print(f"turtle: {len(fs)-len(bad)}/{len(fs)} parsed, {t} triples")
for b in bad: print("  FAIL", *b)
PY

# run the package's own release gate if it ships one
GATE=$(ls 03-tooling/release_check_v*.sh 2>/dev/null | sort -V | tail -1 || true)
if [ -z "${GATE:-}" ]; then
  # fall back to a *gate*.sh, but never an adversarial/negative/test fixture (F4)
  GATE=$(ls 03-tooling/*gate*.sh 2>/dev/null | grep -viE "adversarial|negative|fixture|_test" \
         | sort -V | tail -1 || true)
fi
[ -n "${GATE:-}" ] && echo "gate: $(basename "$GATE") (highest SemVer)"
[ -n "$GATE" ] && { chmod +x "$GATE"; bash "$GATE" | tail -12; }
echo "rehydrated: $WORK/$PKG"
