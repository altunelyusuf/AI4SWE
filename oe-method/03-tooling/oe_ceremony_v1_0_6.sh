#!/usr/bin/env bash
# oe_ceremony_v1_0_6.sh — the session-start ceremony, one order, every session, with a verdict.
#
# v1.0.6 (2026-10-12): the structure check ran without -B and left __pycache__ in repo-tooling, a stowaway that made the NEXT ceremony REFUSE (seen twice this session); it runs with -B now.
#
# v1.0.1: the manifest check excludes PUBLISH_RECORD.ttl, as the publisher's own self-check does. The publisher writes that
# record AFTER the manifest, so a manifest that does not list it (the convention for a published package) made this
# script report the record as a stowaway and REFUSE a correct package (found on repo-tooling v1.21.0, 2026-10-05).
#
# v1.0.2: stage 6 reports the package's own file-structure and naming debt (BP-D53): how many violations it has recorded in the
# debt register, and any NEW violation outside it. It informs; it does not refuse (a package must be able to start work on its own
# debt). The CI gate is what fails a push that adds a violation.
#
# v1.0.3: a handover filed by ANOTHER session into 07-handover-inbox/pending/ is not a stowaway. The filing session cannot update
# this package's manifest (it must not touch another package's files), so every arrival made the manifest check REFUSE until the
# owning session next released (found on oe-pack v20.95.0, 2026-10-06, three arrivals). The unlisted-file check now skips
# 07-handover-inbox/pending/ ; a LISTED file there is still hash-verified, and an unlisted file anywhere else still refuses.
#
# v1.0.5 (plan task 24; observation from the a domain ecosystem session, 2026-10-12): the inbox line counted the OE pack's pending folder INCLUDING its README, and said
# so for every package, so a package with an empty inbox read "2 item(s)". It now prints two lines: the OE pack's inbox (README not counted) and, for any other package, that
# package's own inbox, each with its folder named. Nothing else changed.
#
# v1.0.4: stage 6 reads the governance AGGREGATE (oe-pack/04-documentation/structure-debt/STRUCTURE_DEBT_AGGREGATE_v*.tsv) as the ceiling
# baseline, and only if there is none the older STRUCTURE_DEBT_REGISTER_v* name in the governance package (accepted for one release, as
# the publisher accepts it). Since the owner's ruling of 2026-10-07 (each package carries its own register) the governance package holds
# its OWN register under that older name, so the old glob handed the checker a two-line file as the baseline and every package's ceremony
# ended "FAIL -- a package's own register tried to widen what the governance aggregate records" (found on oe-method v3.5.0, 2026-10-07,
# the first ceremony after the release; the publisher and the CI gate had been moved, this stage had not).
#
# Why this exists. The ceremony B5 prescribes (rehydrate, verify, then check freshness against
# origin) was carried in prose across BOOTSTRAP's STEP 2 / 3 / 4, so each session executed its own
# arrangement of it and reported its own selection of numbers. This runs the whole order in one
# command and prints one verdict, so two sessions' ceremonies are comparable line by line.
#
# What it adds over the prose it replaces (it is strictly stronger, never weaker):
#   - the governing discipline is resolved by highest SemVer BOTH on disk AND on GitHub through the
#     authenticated API, and the local bytes are compared with the remote blob. A local copy that
#     differs from the repository, or a remote version higher than the local one, REFUSES. The
#     prose ceremony read the local file and reported its digest, which proves nothing about the
#     repository (the same internal-consistency gap B5 was enriched to close, one level up).
#   - the access probe is explicit and recorded, so a session states what it could reach instead of
#     inferring a block from one failed request.
#   - a stale checkout REFUSES; it is not a warning.
#   - the manifest check is the stowaway-aware verifier, run from inside the package, never the
#     listed-files-only `sha256sum -c` idiom, which is silent about an unlisted file.
#
# Usage:  bash repo-tooling/oe_ceremony_v1_0_6.sh [package-slug] [--allow-offline]
#         run from the root of the monorepo working copy. Package defaults to repo-tooling.
#         Credentials: `gh api` if present, else curl with $GH_PAT. --allow-offline downgrades the
#         remote comparison to a stated UNVERIFIED line instead of refusing -- it never passes
#         silently, and the verdict says the discipline was not compared with the repository.
set -uo pipefail
export PYTHONDONTWRITEBYTECODE=1   # no helper may leave bytecode in the package (v1.0.6)

PKG="repo-tooling"; OFFLINE=0
for a in "$@"; do
  case "$a" in
    --allow-offline) OFFLINE=1 ;;
    --*) echo "unknown option: $a" >&2; exit 2 ;;
    *) PKG="$a" ;;
  esac
done
REPO="${OE_TARGET_REPO:-your-account/Ontologies}"
FAIL=0; WARN=0
say()  { printf '%s\n' "$*"; }
bad()  { printf 'REFUSE  %s\n' "$*"; FAIL=1; }
note() { printf 'NOTE    %s\n' "$*"; WARN=1; }

# the one API reader: gh if it is there, curl with a token if it is not.
api() { # api <path> ; prints the response body
  if command -v gh >/dev/null 2>&1; then gh api "$1" 2>/dev/null
  elif [ -n "${GH_PAT:-}" ]; then
    curl -sS -H "Authorization: Bearer $GH_PAT" -H "Accept: application/vnd.github+json" \
         "https://api.github.com$1" 2>/dev/null
  else return 1; fi
}
highest() { ls $1 2>/dev/null | sort -V | tail -1; }

say "== OE ceremony v1.0.0 =="
say "repository: $REPO    package: $PKG    date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
[ -d .git ] || { bad "not a git working copy: $(pwd) -- run this from the monorepo root"; exit 1; }
[ -d "$PKG" ] || { bad "no package directory '$PKG' here"; exit 1; }

# ---- 1. ACCESS -------------------------------------------------------------------------------
say ""; say "-- 1. access --"
GIT_OK=0; git ls-remote --exit-code origin HEAD >/dev/null 2>&1 && GIT_OK=1
say "git over the proxy:        $([ $GIT_OK = 1 ] && echo reachable || echo UNREACHABLE)"
[ $GIT_OK = 1 ] || bad "git cannot reach origin; nothing below can be trusted"

API_OK=0; API_JSON="$(api "/repos/$REPO" || true)"
printf '%s' "$API_JSON" | grep -q '"full_name"' && API_OK=1
say "authenticated GitHub API:  $([ $API_OK = 1 ] && echo reachable || echo UNREACHABLE)"
if [ $API_OK = 1 ]; then
  PRIV="$(printf '%s' "$API_JSON" | python3 -c 'import sys,json;d=json.load(sys.stdin);print("private" if d["private"] else "public")' 2>/dev/null || echo "?")"
  say "repository visibility:     $PRIV  (measured, not assumed)"
fi
RAWC="$(curl -sS -o /dev/null -w '%{http_code}' "https://raw.githubusercontent.com/$REPO/main/README.md" 2>/dev/null || echo 000)"
say "unauthenticated raw file:  HTTP $RAWC  $([ "$RAWC" = 200 ] && echo '(readable)' || echo '(expected on a private repository: no credential is sent)')"
say "tag push from a session:   refused by the git proxy (HTTP 403); release tags are made by the"
say "                           'OE tags' workflow on GitHub after the branch push."

# ---- 2. FRESHNESS ----------------------------------------------------------------------------
say ""; say "-- 2. freshness against origin (B5) --"
git fetch -q origin 2>/dev/null
BR="$(git rev-parse --abbrev-ref HEAD)"
read -r AHEAD BEHIND <<<"$(git rev-list --left-right --count "HEAD...origin/$BR" 2>/dev/null || echo '? ?')"
say "branch $BR: $AHEAD ahead, $BEHIND behind origin/$BR"
say "HEAD        $(git rev-parse HEAD)"
say "origin/$BR  $(git rev-parse "origin/$BR" 2>/dev/null || echo '?')"
if [ "$BEHIND" != "0" ]; then bad "the checkout is stale ($BEHIND behind). git pull --rebase, then run this again."; fi
DIRTY="$(git status --porcelain --untracked-files=no | wc -l | tr -d ' ')"
[ "$DIRTY" = "0" ] || note "$DIRTY tracked file(s) modified in the working copy"

# ---- 3. DISCIPLINE VERSION, COMPARED WITH THE REPOSITORY -------------------------------------
say ""; say "-- 3. governing discipline, resolved by version and compared with the repository --"
compare_governed() { # compare_governed <dir> <glob> <label>
  local dir="$1" glob="$2" label="$3"
  local loc; loc="$(highest "$dir/$glob")"
  if [ -z "$loc" ]; then bad "$label: nothing matching $dir/$glob on disk"; return; fi
  local lsha; lsha="$(sha256sum "$loc" | cut -d' ' -f1)"
  say "$label"
  say "  local  $(basename "$loc")  sha256 $lsha"
  local listing; listing="$(api "/repos/$REPO/contents/$dir" || true)"
  if ! printf '%s' "$listing" | grep -q '"name"'; then
    if [ $OFFLINE = 1 ]; then note "  remote UNVERIFIED: the API could not be read (--allow-offline)";
    else bad "  the API could not be read, so the local copy was never compared with the repository"; fi
    return
  fi
  local rname
  rname="$(printf '%s' "$listing" | PAT="$glob" python3 -c '
import sys,json,os,re,fnmatch
pat=os.environ["PAT"]
names=[x["name"] for x in json.load(sys.stdin) if fnmatch.fnmatch(x["name"],pat)]
key=lambda n:[int(i) for i in re.findall(r"\d+",n)]
print(sorted(names,key=key)[-1] if names else "")' 2>/dev/null)"
  if [ -z "$rname" ]; then bad "  no $glob found in $dir on the repository"; return; fi
  local rsha
  rsha="$(api "/repos/$REPO/contents/$dir/$rname" | python3 -c '
import sys,json,base64,hashlib
d=json.load(sys.stdin); print(hashlib.sha256(base64.b64decode(d["content"])).hexdigest())' 2>/dev/null || true)"
  say "  remote $rname  sha256 ${rsha:-UNREADABLE}"
  if [ "$rname" != "$(basename "$loc")" ]; then
    bad "  version mismatch: the repository's highest is $rname, this checkout resolves $(basename "$loc")"
  elif [ -z "$rsha" ]; then
    if [ $OFFLINE = 1 ]; then note "  remote blob UNVERIFIED (--allow-offline)"; else bad "  the remote blob could not be read"; fi
  elif [ "$rsha" != "$lsha" ]; then
    bad "  the local copy differs from the repository -- do not act on it"
  else
    say "  identical to the repository (byte comparison of the decoded blob)"
  fi
}
compare_governed "oe-method/04-documentation"               "OE_Operating_Discipline_v*.md"  "OE Operating Discipline"
compare_governed "a registrant package/04-documentation" "LINEAGE_OPERATING_DISCIPLINE_v*.md" "Lineage Operating Discipline"

# ---- 4. COUNTS -------------------------------------------------------------------------------
say ""; say "-- 4. counts --"
VER="$(tr -d ' \n\r' < "$PKG/VERSION.txt" 2>/dev/null || echo '?')"
MF="$(cd "$PKG" && highest 'MANIFEST_SHA256*.txt')"
LISTED="$(grep -v '^#' "$PKG/$MF" 2>/dev/null | grep -c . || echo 0)"
FILES="$(cd "$PKG" && find . -type f ! -path './.git/*' | wc -l | tr -d ' ')"
say "$PKG v$VER   manifest $MF lists $LISTED file(s); $FILES file(s) on disk"
# INBOX-COUNT-BEGIN (the test slices this block)
inbox_count() { ls "$1" 2>/dev/null | grep -v '^README\.md$' | wc -l | tr -d ' '; }
say "OE inbox pending (oe-pack/07-handover-inbox/pending): $(inbox_count oe-pack/07-handover-inbox/pending) item(s)  (G39: read them before working)"
if [ "$PKG" != "oe-pack" ]; then say "this package's own inbox pending ($PKG/07-handover-inbox/pending): $(inbox_count "$PKG/07-handover-inbox/pending") item(s)"; fi
# INBOX-COUNT-END
[ "$VER" = "?" ] && bad "$PKG has no readable VERSION.txt"
[ -z "$MF" ] && bad "$PKG ships no MANIFEST_SHA256*.txt"

# ---- 5. MANIFEST, STOWAWAY-AWARE -------------------------------------------------------------
say ""; say "-- 5. manifest (stowaway-aware) --"
VM="$(highest 'repo-tooling/verify_manifest_v*.py')"
if [ -z "$VM" ] || [ -z "$MF" ]; then bad "cannot run the manifest check"; else
  say "verifier: $(basename "$VM")"
  ( cd "$PKG" && python3 "../$VM" "$MF" --exclude PUBLISH_RECORD.ttl --exclude '07-handover-inbox/pending/*' ) | tail -4 | sed 's/^/  /'
  [ "${PIPESTATUS[0]:-0}" = "0" ] || bad "manifest check did not pass for $PKG"
fi

# ---- 6. FILE STRUCTURE AND NAMING (BP-D53), THIS PACKAGE ONLY --------------------------------
say ""; say "-- 6. file structure and naming (BP-D53) --"
SC="$(highest 'repo-tooling/oe_structure_check_v*.py')"; REG="$(highest 'oe-pack/04-documentation/structure-debt/STRUCTURE_DEBT_AGGREGATE_v*.tsv')"; [ -n "$REG" ] || REG="$(highest 'oe-pack/04-documentation/structure-debt/STRUCTURE_DEBT_REGISTER_v*.tsv')"
if [ -z "$SC" ] || [ -z "$REG" ]; then note "  structure check or debt register not found; not reported"; else
  OUT="$(python3 -B "$SC" . --package "$PKG" --register "$REG" 2>&1)"; RC=$?
  printf '%s\n' "$OUT" | grep -E "^examined|^register|^  NEW|^VERDICT" | sed 's/^/  /'
  [ $RC = 0 ] || note "  this package has a file-structure or naming violation outside the register; fix it or the CI gate will fail the push"
fi

# ---- verdict ---------------------------------------------------------------------------------
say ""
if [ $FAIL = 0 ]; then
  say "VERDICT: PROCEED   discipline $(basename "$(highest 'oe-method/04-documentation/OE_Operating_Discipline_v*.md')") sha256 $(sha256sum "$(highest 'oe-method/04-documentation/OE_Operating_Discipline_v*.md')" | cut -c1-16)…, $PKG v$VER, $BEHIND behind origin$([ $WARN = 1 ] && echo ' (with notes above)')"
  exit 0
else
  say "VERDICT: REFUSE    the lines marked REFUSE above must be cleared before any governed action"
  exit 1
fi
