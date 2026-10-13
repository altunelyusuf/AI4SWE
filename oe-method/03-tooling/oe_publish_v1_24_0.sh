#!/usr/bin/env bash
# oe_publish_v1_24_0.sh — publish a governed package into your-account/Ontologies.
# v1.24.0 (2026-10-12): no helper may write bytecode into the clone (found by running a dry-run on a clean tree: repo-tooling/__pycache__ appeared).
# v1.23.0 (plan task 24; two observations from the a domain ecosystem session, 2026-10-12): (1) the deletion guard pairs the files of one stem by exact path FIRST, then supersedes the newest
# unmatched origin version with a source file, so with five versions at origin and one kept it names the four that go and never the kept file (it used to pair them in name order and
# named the kept v1_4_0 in place of v1_0_0). (2) the wholesale-replace refusal now says which listed files origin's own latest manifest does NOT list (filed there after its last
# release, most likely another session's handover: refresh the stage) apart from those it lists and the stage no longer holds (removed by the stage, to be named with --expect-delete). No check was added, removed or loosened.
# v1.22.0 (plan task 21): the governing pack is the DIRECT sibling ../oe-pack, else the only one a folder down; several candidates give none and the caller is told to name one (OE_UPSTREAM). The old first-match glob over ../*/oe-pack bound whichever stale pack sorted first and refused a good release.
# v1.21.0 (plan v1.7.0 task 18): the package gate that needs the governing pack is handed an ABSOLUTE path. A gate that changes into the package folder before it reads --upstream resolved the relative sibling path (../oe-pack) against its own root and reported a false OUT OF ACCORDANCE, so every method release was refused until OE_UPSTREAM was set by hand.
# v1.20.0 (plan v1.3.0 task 12; BP-D7): a file whose name carries a version token and exists at origin under the same name and path with DIFFERENT bytes
# is refused (named). BP-D7 says a changed file gets a new version; until now only the package version was checked, so a changed file kept its name
# unrefused (found twice: a plan file edited in place in oe-pack, and three scripts and a lineage register under unchanged names in another package,
# 2026-10-11). A rewrite that is meant (a typo in a record's own header, say) is named in a file, one path per line, given with --expect-rewrite <file>
# or OE_EXPECT_REWRITE_FILE=<file>; exactly the listed paths pass, a listed path that was not rewritten refuses (the same discipline as --expect-delete).
# Files without a version token in their name (README.md, VERSION.txt, HANDOVER_LOG.md) and folders named fixtures are not examined.
# v1.19.0 (plan v1.16.0, owner 2026-10-07: shorter runs): every refusal that a session can clear says the command that clears it. Changed: the manifest
# check names oe_manifest, the "already published" refusal names the two edits, the structure refusal names the listing command, and the wholesale-replace
# refusal no longer points at --force (which accepts every deletion unseen) but at --expect-delete, with oe_release's --deletions-file that writes the list.
# No check was added, removed or loosened.
# v1.16.0 (plan v1.14.0 item 55): the named-deletion guard no longer lets a same-named file elsewhere hide a deletion. Until now a file counted
# as deleted only if its version-stripped name was absent from the WHOLE source, so deleting archive/x_v1_0_0.ttl while a file called x_v*.ttl
# stayed anywhere else in the package was reported as nothing (found 2026-10-07 while moving a snapshot). The guard now counts: per
# version-stripped name, origin files that stay in their own folder are matched first; what is left over in origin is paired with what is left
# over in the source (a file MOVED between folders, v1.5.7, still pairs), and only origin files with no partner are deletions.
# v1.15.0 (plan v1.10.0 item 38(b)): the Turtle parse and the structure check read what they skip from the ONE class table, OE_STRUCTURE_CLASSES_v*.tsv,
# held by the governance clone, through oe_structure_classes_v*.py (the reader the release check and the structure check also use). The
# governance clone is made before the parse for that reason (it was made after it). Without the reader or the table the parse falls back to
# the two folders it always skipped, and says so; a table that exists and is unreadable stops the publish.
# v1.12.1: the structure step reads the debt register of the package being published when that package is oe-pack, if its own
# highest register is at least as new as the one the governance clone holds. The register lives in oe-pack, so a release of oe-pack
# that renames a file carrying recorded debt (the membership step of the OEE consolidation renamed 48) could never pass: the
# register in the clone still named the old file, which reported it CLEARED and the new name NEW. The register travels in the same
# commit and is reviewed with it; for every other package the governance clone's register is still the only one read.
# v1.12.0: --expect-delete <file>, the named-deletion override (L-126). --force answered the wholesale-replace guard with "accept every
# deletion", so a file another session filed between the reading and the publish was removed with the rest (found 2026-10-05: a second
# inbox request was deleted by a publish that had only been meant to move one). The new option takes a list of paths (relative to the
# package, one per line, `#` comments allowed) and accepts exactly those: any deletion not on the list REFUSES (named), and any listed
# path that is not a deletion REFUSES too (a typo, or a file already gone, must not pass silently). It is for changes that really remove
# files, such as the consolidation of a package's files; --force stays for compatibility, prints a warning, and cannot be combined with it.
#
# v1.10.1: the TAG NOTICE text. v1.9.1 made a refused tag push non-fatal but still told the session
# to push the tag itself from "a session or machine that can". Since 2026-10-05 that is the wrong
# instruction: tag pushes from a session are refused as a matter of policy (HTTP 403 on the push
# leg, branch pushes to the same repository succeed -- re-measured 2026-10-05 on a throwaway tag),
# and the 'OE tags' workflow makes the release tag on GitHub's side after the branch push. The
# notice now says that, says how to confirm it (ls-remote after the workflow runs), and says what
# to do when the repository has not adopted the workflow: ask for it, do not push by hand.
#
# v1.10.0: OE_PACKAGE_DIR — the package may be published into a NAMED subfolder of the target
# repository. Until now the destination inside the target was derived from the slug ($SLUG/) or was
# the whole repository (OE_PACKAGE_AT_ROOT=1), and neither fits a package that owns a named folder
# of a repository it does not own entirely. Found on mastering-bitcoin-3e (2026-10-05), which moved
# out of the monorepo into your-account/mastering-bitcoin at 3e/ — one folder per edition of the
# book, so the package is neither at the root nor at a folder named after itself. The workaround
# available before this was to pass "3e" as the slug, which publishes to the right folder but makes
# the slug the package's identity everywhere the record uses it: dcterms:identifier "3e", the pkg:
# namespace http://example.org/3e/publish#, the record's own label and the release tag. Identity is
# not the same question as location (OE B4), so they are now two variables: the slug stays the
# package's name and OE_PACKAGE_DIR says where in the target it lives. Unset, nothing changes —
# every existing caller keeps publishing to $SLUG/ or, with OE_PACKAGE_AT_ROOT=1, to the root; the
# two are now the default and a special case of one explicit setting. The copy step, which still
# named $SLUG directly in four places where it meant the destination, now names $PKG_DIR.
#
# v1.9.1: a tag that cannot be pushed no longer aborts the run after the commit is already
# published. Found on oe-method v2.34.0 (2026-10-05): the session's network path refused tag
# pushes, `set -e` stopped the script at the tag, and the mirror step after it never ran -- the
# mirror went stale with no notice, the exact failure the mirror notice exists to prevent. The
# commit is the release; the tag is its label. A failed tag push now prints a TAG NOTICE naming the
# tag and commit and the run continues to the mirror step.
#
# v1.9.0: the publish commit ends with a `Session-Usage:` trailer when the session usage tool sits
# beside this script (oe_session_usage_v*.py, highest version) and can measure the session. A
# session that ends by publishing has no commit of its own to carry its usage record, so the
# publisher carries it; `--summarise` reads it back from history. Measuring never blocks a publish:
# if the tool is absent or refuses, the commit simply has no usage trailer and a note says why.
#
# v1.5.4: REPO and the git commit identity were hardcoded, meaning oe-method's own "cleaned,
# distributed" copy shipped the real account name and personal identity to every collaborator
# who received it -- caught on direct challenge, not found independently. Parameterized both via
# OE_TARGET_REPO / OE_GIT_NAME / OE_GIT_EMAIL, defaulting to the real values for this operator's
# own use. The generalisation transform that derives oe-method's copy already replaces the real
# account and personal identity wherever they appear in prose (it always did); the previous
# v1.5.3 needed an OPERATIONAL_FILES exception in the clean gate specifically because the
# hardcoded values were load-bearing for the script's OWN function, not because the gate itself
# was wrong. Parameterizing removes the need for that exception entirely -- the generic default
# a collaborator receives is a harmless placeholder they're expected to override, and this
# operator's own real values are supplied via environment at call time, not baked into the file.
#
# v1.8.2: v1.8.0 wrote the governance repository's full name into every record; in oe-method, the
# distributable copy, that is the account data its own clean gate forbids -- missed because package
# gates run before the record is written, so oe-method v2.31.0's record carried it. Same-repository
# publishes now cite "(this repository)"; publishes into other repositories keep the full name.
#
# v1.8.1: owner ruling (2026-09-24) -- in a repository readable by people who cannot read the private
# governance (for example students reading a course repository), governance provenance is a citation
# for the governance owner, not something readers are expected to verify, and no governing text is
# copied in. The publisher now MEASURES the governance repository's visibility at publish time and
# writes it, with that statement, into every publish record, so the choice is explicit, not implied.
#
# v1.8.0: publishing into standalone repositories (owner ruling: OEE's work, blocking every course
# repository). (1) The discipline and knowledge base are read from the governance repository
# (OE_GOVERNANCE_REPO / OE_GOVERNANCE_PATH, default Ontologies / oe-method), cloned separately at a
# recorded commit -- never from inside the target. (2) OE_PACKAGE_AT_ROOT=1 publishes a package that
# is the whole target repository. (3) Every publish record carries full governance provenance:
# repository, folder, commit, discipline file, and knowledge-base digest. OE_TARGET_URL overrides the
# target location (used for testing against a local repository). Monorepo publishing is unchanged.
#
# v1.10.2: the Turtle parse skips folders named fixtures and archive (a deliberately broken negative fixture made oe-pack unpublishable).
# v1.7.1: the mirror step ran after the temporary clone -- its working directory -- was deleted,
# so git and python both failed at start-up; found on v1.7.0's first real publish (oe-method
# v2.29.0), which correctly reported the failure instead of passing. It now changes to a stable
# directory first.
#
# v1.7.0: after publishing oe-method, the publisher now syncs the standalone mirror
# (oe_mirror_sync_v1_0_0.sh) in the same run, and opens or refreshes a GitHub issue on the source
# repository when that sync cannot complete. Owner direction, 2026-09-24.
#
# v1.6.0: the discipline and knowledge base the ceremony records are now read from oe-method
# (04-documentation, 01-vocabularies), not oe-pack -- owner direction, 2026-09-24: oe-pack stays
# the private development source that carries the history; oe-method is the location links point
# to. The upstream a package derives from (line ~171) is deliberately unchanged: oe-method is
# still derived FROM oe-pack. Tested by dry-run before shipping.
#
# v1.5.9: a real, self-implicating finding (agentic-sdlc -> OE, 2026-09-21): v1.5.8's own new
# stowaway check had no exclusion for PUBLISH_RECORD.ttl, which is generated by this very
# publish process AFTER the manifest step runs and so can never legitimately be pre-listed --
# meaning every package publishing for the first time through the new check would fail on a
# file this same script creates. Not caught earlier because every package this session had
# already published carried PUBLISH_RECORD.ttl from a prior cycle, masking the gap. Fixed with
# verify_manifest_v1_1_0.py's new manifest-declared exemption mechanism (a `# EXEMPT: <path>`
# comment line in the manifest itself, for a package's own structurally-necessary files such as
# a manifest-digest carrier) plus a hardcoded --exclude for PUBLISH_RECORD.ttl here, since it is
# this script's own universal convention, not a package-specific one. Tested both directions
# (a declared exemption is respected; an undeclared stowaway is still caught) before this step
# was made to depend on the new version.
#
# v1.5.8: step 1's manifest self-check used `sha256sum -c`, which only verifies files the
# manifest LISTS -- a file present on disk but not listed (a stowaway) passed silently. Real
# cross-session finding (fizyovibe-admin -> OE, 2026-09-13, Finding 2), independently reproduced
# before fixing: a synthetic stowaway file passed the check unchanged, reported alongside files
# that genuinely verified. The exact same blind spot was independently confirmed in the
# governing session's own inline-Python equivalent, used throughout that session's manifest
# checks. Fixed by replacing the idiom with verify_manifest_v1_0_0.py (new, co-located file),
# which checks both directions: every listed file verifies, AND every real file on disk is
# listed. Tested to discriminate both ways (a stowaway case correctly fails, a clean case
# correctly passes) before this step was made to depend on it, then cross-checked against the
# old inline-Python method on a real package tree to confirm no regression in the tampering
# check itself.
#
# v1.5.7: v1.5.6's stem was directory-qualified, so a file MOVED between directories -- the one
# thing every handover inbox does, disposing a proposal from pending/ to accepted/ or rejected/
# -- read as a deletion. Caught by a real cross-session finding (a registrant package,
# 2026-09-10) when the guard refused a completely ordinary inbox-processing publish. Fixed by
# matching on the version-stripped BASENAME alone rather than the directory-qualified stem (see
# step 4c below for the full comment); the directory-qualified path is still what gets reported,
# so a genuine deletion is named precisely.
#
# v1.5.6: v1.5.5's wholesale-replace guard used a plain file-list diff, which flagged this
# session's OWN routine version bumps -- an old-versioned file $SRC has already superseded (e.g.
# foo_v1_0_0.ttl replaced by foo_v1_1_0.ttl) looks identical, from a bare diff, to a file another
# session added that this session never touched. Caught immediately, not found independently:
# this exact publish's own dry run refused a normal version bump on its very first real use.
# Fixed with a stem match (see step 4c below for the full comment) -- a file superseded by a
# newer version of itself in $SRC is recognised and not flagged; only a file whose stem has no
# counterpart anywhere in $SRC is treated as a genuine, unexplained addition.
#
# v1.5.5: a real cross-session finding (a registrant package, 2026-09-09) traced a silent
# data-loss bug to step 5: it clones origin fresh, then replaces the package directory wholesale
# with $SRC, with no comparison of what origin currently holds against what $SRC has. Any file
# origin gained under the package directory after $SRC was taken -- the common case is another
# session's own inbox filing landing between this session's prepare and publish steps -- was
# silently deleted, and the publish record still reported PASS. Reproduced from the two commits
# the finding named before building this fix, not assumed from the report alone. Added a
# wholesale-replace guard (step 4c): before the replace, diff origin's current file list under
# the package directory against $SRC's; if origin has files $SRC lacks, REFUSE and name them,
# unless --force is passed (sharing $4 with --dry-run), in which case the deletion count is
# recorded in the publish record (pub:deletedFilesCount) as an explicit, auditable override
# rather than a silent one. Tested directly (not just syntax-checked): a real divergence is
# detected and correctly named; no divergence produces zero false positives; a brand-new package
# with nothing yet at origin is handled safely.
#
# v1.5.3: TTL_TOTAL/TTL_PARSED used a fragile '"'"' single-quote-escape sequence inside an
# inline python -c string, which a real cross-session finding traced to a corrupted glob
# pattern (repr() showed the pattern itself carried extra literal quote characters, matching
# nothing -- PUBLISH_RECORD.ttl recorded turtleParsed/turtleTotal 0 for 11 of 14 packages while
# the same run's own step-2 output counted them correctly). Reproduced independently before
# fixing, not trusted from the report alone. Replaced with a heredoc, which needs no nested
# quote-escaping at all; verified the fix from both the package's own directory and a different
# CWD (matching this script's own later `cd "$TMP.repo"`), since the original bug's exact
# trigger was never fully explained and a CWD-dependent regression would be worse than the
# original, always-wrong-in-the-same-way defect.
#
#   bash repo-tooling/oe_publish_v1_24_0.sh <token> <source-dir> <package-slug> [--dry-run] [--force | --expect-delete <file>] [--expect-rewrite <file>]
#   OE_PACKAGE_DIR=<folder in the target>   (default: the slug; OE_PACKAGE_AT_ROOT=1 for the root)
#
# e.g. bash repo-tooling/oe_publish_v1_24_0.sh $GH /home/claude/build/snlif-v1_4_0 snlif
#      OE_PACKAGE_DIR=3e bash repo-tooling/oe_publish_v1_24_0.sh $GH /home/claude/mastering-bitcoin/3e mastering-bitcoin-3e
#
# Verifies BEFORE it pushes: manifest self-check, Turtle parse, the package's own
# release gate if it ships one, and a BP-D7 guard that refuses to overwrite an equal
# or newer published version. Nothing reaches GitHub unless every check passes.
#
# v1.5.1 (PATCH): SRC's .git (present when SRC is itself a session's git clone) is now
# excluded from the copy into $SLUG/ — previously it created an embedded-repo GITLINK
# (git tree mode 160000) instead of real files, so the published subfolder looked
# committed but was empty on any fresh clone. --dry-run structurally cannot catch this:
# it returns before the clone-and-copy step ever runs. Caught on oe-method v2.8.0's
# first real (non-dry-run) publish.
#
# v1.5.2 (PATCH): v1.5.1 alone was insufficient. Once a path is committed as a gitlink,
# git treats it as submodule-managed and `git add -A` silently ignores its on-disk
# contents even after real files replace it — no .gitmodules exists to tell git
# otherwise. oe-method v2.8.1's first publish attempt under v1.5.1 reported "nothing to
# commit, working tree clean" with real files sitting right there. Added `git rm -r
# --cached "$SLUG"` before the add, verified by manually reproducing the copy in a
# scratch clone first (a diagnosis grounded in bytes, not assumed from the symptom).
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1   # v1.24.0: the structure step loads repo-tooling libraries with importlib and left __pycache__ in the clone (a stowaway the next ceremony refused)
# v1.6.0: resolved ONCE, before any cd -- recomputing it later, relative to a changed working
# directory, sent the companion-file lookups into the temp clone when the script was invoked by a
# relative path, and the publisher exited silently.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

TOKEN="${1:?usage: oe_publish_v1_24_0.sh <token> <source-dir> <package-slug> [--dry-run] [--force | --expect-delete <file>] [--expect-rewrite <file>]}"
# Session attribution. Self-declared and unverified: this records who SAYS they made the change,
# which is what diagnosing ParallelSessionLineageFork and CrossSessionContamination needs. An
# absent declaration is recorded as 'unattributed' and warned about — never inferred from the git
# author, which several sessions share.
SESSION="${OE_SESSION:-unattributed}"
[ "$SESSION" = "unattributed" ] && echo "WARNING: OE_SESSION unset — this publish will be recorded as unattributed" >&2
SRC="${2:?source dir required}"
SLUG="${3:?package slug required}"
DRY=""; FORCE=""; EXPECT_FILE=""; REWRITE_FILE="${OE_EXPECT_REWRITE_FILE:-}"
ARGV=("${@:4}"); AI=0
while [ "$AI" -lt "${#ARGV[@]}" ]; do
  case "${ARGV[$AI]}" in
    --dry-run) DRY="--dry-run" ;;
    --force) FORCE="--force" ;;
    --expect-delete) AI=$((AI+1)); EXPECT_FILE="${ARGV[$AI]:-}"; [ -n "$EXPECT_FILE" ] || { echo "REFUSED: --expect-delete needs a file of paths" >&2; exit 2; } ;;
    --expect-rewrite) AI=$((AI+1)); REWRITE_FILE="${ARGV[$AI]:-}"; [ -n "$REWRITE_FILE" ] || { echo "REFUSED: --expect-rewrite needs a file of paths" >&2; exit 2; } ;;
    *) echo "REFUSED: unknown argument '${ARGV[$AI]}'" >&2; exit 2 ;;
  esac
  AI=$((AI+1))
done
if [ -n "$FORCE" ] && [ -n "$EXPECT_FILE" ]; then echo "REFUSED: --force accepts every deletion and --expect-delete accepts only the listed ones; use one" >&2; exit 2; fi
if [ -n "$EXPECT_FILE" ] && [ ! -f "$EXPECT_FILE" ]; then echo "REFUSED: --expect-delete file not found: $EXPECT_FILE" >&2; exit 2; fi
if [ -n "$REWRITE_FILE" ] && [ ! -f "$REWRITE_FILE" ]; then echo "REFUSED: --expect-rewrite file not found: $REWRITE_FILE" >&2; exit 2; fi
REPO="${OE_TARGET_REPO:-your-account/Ontologies}"
# v1.8.0: governance is read from its own repository, never from inside the target; a target may be
# a standalone repository whose package sits at its root.
TARGET_URL="${OE_TARGET_URL:-https://x-access-token:${TOKEN}@github.com/${REPO}.git}"
GOV_REPO="${OE_GOVERNANCE_REPO:-your-account/Ontologies}"
GOV_PATH="${OE_GOVERNANCE_PATH:-oe-method}"
GOV_URL="${OE_GOVERNANCE_URL:-https://x-access-token:${TOKEN}@github.com/${GOV_REPO}.git}"
# v1.10.0: where the package lives INSIDE the target repository. Three ways to say it, most
# explicit first: OE_PACKAGE_DIR names the folder; OE_PACKAGE_AT_ROOT=1 means the package is the
# whole repository; otherwise it is a folder named after the slug, which is the old default. A
# leading "./" or a trailing "/" is tolerated and stripped, and an absolute path is refused --
# the value is a path inside the target, never on this machine.
if [ -n "${OE_PACKAGE_DIR:-}" ]; then
  PKG_DIR="${OE_PACKAGE_DIR#./}"; PKG_DIR="${PKG_DIR%/}"
  case "$PKG_DIR" in
    /*|*..*|"") echo "REFUSED: OE_PACKAGE_DIR must be a relative path inside the target repository, not '${OE_PACKAGE_DIR}'" >&2; exit 1 ;;
  esac
elif [ "${OE_PACKAGE_AT_ROOT:-0}" = "1" ]; then PKG_DIR="."
else PKG_DIR="$SLUG"; fi
TMP="/tmp/oe_publish_$$"
trap 'rm -rf "$TMP".* 2>/dev/null || true' EXIT

fail() { echo "REFUSED: $*" >&2; exit 1; }

[ -d "$SRC" ] || fail "source dir not found: $SRC"
[ -f "$SRC/VERSION.txt" ] || fail "no VERSION.txt in $SRC — a governed package must declare its version"
VER=$(tr -d ' \n\r' < "$SRC/VERSION.txt")
echo "== $SLUG v$VER from $SRC =="

# ---- 1. manifest self-check (v1.5.8: stowaway-checking, not just tampering) ----
# A real cross-session finding (fizyovibe-admin -> OE, 2026-09-13), independently reproduced
# before fixing, not accepted from the report alone: the `sha256sum -c` idiom this step used to
# run only verifies files the manifest LISTS. A file present on disk but not listed -- a
# stowaway -- passes silently, reported as "N/N" alongside files that genuinely verify. The
# exact same blind spot was independently confirmed in this repo's own inline-Python equivalent,
# used throughout the governing session's own manifest checks. verify_manifest_v1_0_0.py checks
# both directions and is tested to discriminate both ways before this step trusts it.
cd "$SRC"
MF=$(ls MANIFEST_SHA256*.txt 2>/dev/null | sort -V | tail -1) || true
[ -n "${MF:-}" ] || fail "no MANIFEST_SHA256*.txt in $SRC"
python3 "$HERE/verify_manifest_v1_1_0.py" "$MF" --root . --exclude 'PUBLISH_RECORD.ttl' || fail "manifest self-check failed (see output above) -- rewrite it, do not edit it: python3 repo-tooling/oe_manifest_v1_0_0.py <stage> (removes bytecode and the old manifest, writes the new one, verifies it)"
N=$(grep -v '^#' "$MF" | grep -c .)
OK=$N  # verify_manifest_v1_1_0.py already exited 0 above, meaning all $N listed files verified and no stowaway exists

# ---- 1b. the governance clone, and the ONE class table it holds (v1.15.0) ----
rm -rf "$TMP.gov"
git clone -q --depth 1 "$GOV_URL" "$TMP.gov" || fail "cannot clone the governance repository $GOV_REPO"
GOV_COMMIT=$(git -C "$TMP.gov" rev-parse HEAD)
OE_CLASSES_LIB=$(ls "$HERE"/oe_structure_classes_v*.py 2>/dev/null | grep -v _test_ | sort -V | tail -1 || true)
OE_CLASSES_TABLE=""
if [ -n "${OE_CLASSES_LIB:-}" ]; then
  OE_CLASSES_TABLE=$(python3 -B -I - "$OE_CLASSES_LIB" "$TMP.gov" <<'PYFIND'
import importlib.util, sys
sp = importlib.util.spec_from_file_location("c", sys.argv[1]); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
print(m.find(sys.argv[2]) or "")
PYFIND
) || fail "the class table in the governance clone is unreadable"
fi
export OE_CLASSES_LIB OE_CLASSES_TABLE

# ---- 2. Turtle parse ----
python3 - <<'PY' || fail "Turtle parse failed"
import glob, sys, rdflib
# v1.10.2: a folder named fixtures or archive holds deliberate test inputs and retired records, not shipped
# vocabulary. A deliberately broken fixture (a negative test) made oe-pack unpublishable; those folders are
# counted and reported, not read. Every other Turtle file must parse.
import os
# v1.15.0: the folders not read come from the class table (rows whose publish action is skip); without the reader, the two
# folders this step always skipped
skipdirs = {'fixtures', 'archive'}; tname = 'built-in lists (no class table reader)'
if os.environ.get('OE_CLASSES_LIB'):
    import importlib.util
    _sp = importlib.util.spec_from_file_location('oe_structure_classes', os.environ['OE_CLASSES_LIB']); _m = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(_m)
    _t = _m.load('.', os.environ.get('OE_CLASSES_TABLE') or None)
    skipdirs = _t.publish_skip_dirs(); tname = os.path.basename(_t.path) if _t.path else 'built-in lists (no class table found)'
print('class table: ' + tname)
allf = glob.glob('**/*.ttl', recursive=True)
fs = [f for f in allf if not skipdirs & set(f.split(os.sep)[:-1])]
bad = []; t = 0
for f in fs:
    try:
        g = rdflib.Graph(); g.parse(f); t += len(g)
    except Exception as e:
        bad.append((f, str(e)[:60]))
print(f"turtle: {len(fs)-len(bad)}/{len(fs)} parsed, {t} triples ({len(allf)-len(fs)} fixture or archive file(s) not read)")
for b in bad: print("  FAIL", *b)
sys.exit(1 if bad else 0)
PY

# ---- 2a. GATE RECEIPT (repo-tooling v1.45.0, rule R9) ----
# The package's own gates (2b, 3) can take many minutes and the dry-run and the real publish used to
# run them twice on the same bytes. A receipt binds a pass to the exact bytes of the stage, the extra
# tree a gate reads (the upstream oe-pack), the head of the target repository, the Python version and
# an age limit. Any change makes it invalid and the gates run in full. OE_FRESH_GATES=1 ignores it.
RECEIPT_TOOL=$(ls "$HERE"/oe_gate_receipt_v*.py 2>/dev/null | sort -V | tail -1 || true)
# which governing pack the package gate reads (plan task 21): OE_UPSTREAM if given; else the pack that is a DIRECT sibling of the stage; else a
# single pack one folder down; several candidates give none (the caller is told to name one) -- the old first-match glob bound a stale pack silently
resolve_upstream() {
  local u="${OE_UPSTREAM:-}" c
  if [ -n "$u" ]; then echo "$u"; return 0; fi
  if [ -d ../oe-pack ]; then echo ../oe-pack; return 0; fi
  c=$(ls -d ../*/oe-pack 2>/dev/null || true)
  if [ -n "$c" ] && [ "$(printf '%s\n' "$c" | wc -l)" -eq 1 ]; then echo "$c"; fi
  return 0
}
UPX=$(resolve_upstream)
RC_ARGS=(); [ -n "$UPX" ] && RC_ARGS=(--extra "$UPX")
ORIGIN_HEAD=$(git ls-remote "$TARGET_URL" HEAD 2>/dev/null | cut -f1 || true)
GATES_REUSED=0; GATES_RAN=0; GATE_T0=$(date +%s)
if [ -z "${OE_FRESH_GATES:-}" ] && [ -n "$RECEIPT_TOOL" ] && [ -n "$ORIGIN_HEAD" ] \
   && python3 -B "$RECEIPT_TOOL" check "$SRC" --origin "$ORIGIN_HEAD" ${RC_ARGS[@]+"${RC_ARGS[@]}"} >"$TMP.receipt" 2>&1; then
  GATES_REUSED=1; echo "package gates: reused receipt -- $(tail -1 "$TMP.receipt")"
fi

if [ "$GATES_REUSED" = "0" ]; then
# ---- 2b. THE PACKAGE'S OWN GATES MUST PASS (repo-tooling v1.5.0; v1.19.0: a gate that needs its upstream and cannot find it REFUSES instead of skipping, plan v1.0.0 task 5) ----
# Added after oe-method shipped three releases with its own gates red. The publisher had never
# been invoked for that package — every release was raw git push — and even when invoked it ran
# only a release_check script, never the package's gate directory. A gate a release can bypass
# is not a control; the same reasoning that made attribution mandatory applies here.
if [ -d 05-gates ]; then
  GATE_FAIL=0
  for G in 05-gates/*.py; do
    [ -f "$G" ] || continue
    if grep -q -- '--upstream' "$G" 2>/dev/null; then
      UP=$(resolve_upstream)
      if [ -n "$UP" ]; then
        UP=$(cd "$UP" && pwd)        # absolute: a gate that changes folder must not resolve a relative path against its own root (plan task 18)
        python3 "$G" --upstream "$UP" . >/dev/null 2>&1 || { echo "  GATE FAILED: $(basename "$G")" >&2; GATE_FAIL=1; }
      elif [ -n "${OE_ALLOW_SKIP_UPSTREAM_GATE:-}" ]; then
        echo "  GATE NOT RUN (OE_ALLOW_SKIP_UPSTREAM_GATE is set): $(basename "$G") -- no upstream found; say so in the release summary" >&2
      else
        echo "  GATE CANNOT RUN: $(basename "$G") needs the governing pack and none (or more than one) was found. Put oe-pack (and repo-tooling) as sibling folders of the stage, or name it with OE_UPSTREAM=<dir>. A gate a release can skip is not a control." >&2
        GATE_FAIL=1
      fi
    else
      python3 "$G" . >/dev/null 2>&1 || { echo "  GATE FAILED: $(basename "$G")" >&2; GATE_FAIL=1; }
    fi
  done
  [ "$GATE_FAIL" = "0" ] || fail "the package's own gates in 05-gates/ do not pass — fix the artifact, not the report"
  echo "package gates: all pass"; GATES_RAN=1
fi

# ---- 3. the package's own release gate, if it ships one ----
GATE=$(ls 03-tooling/release_check_v*.sh 2>/dev/null | sort -V | tail -1 || true)
if [ -z "${GATE:-}" ]; then
  # fall back to a *gate*.sh, but never an adversarial/negative/test fixture (F4)
  GATE=$(ls 03-tooling/*gate*.sh 2>/dev/null | grep -viE "adversarial|negative|fixture|_test" \
         | sort -V | tail -1 || true)
fi
[ -n "${GATE:-}" ] && echo "gate: $(basename "$GATE") (highest SemVer)"
if [ -n "${GATE:-}" ]; then
  chmod +x "$GATE"
  bash "$GATE" > "$TMP.gate" 2>&1 || { tail -20 "$TMP.gate"; fail "package release gate did not pass"; }
  tail -3 "$TMP.gate"; GATES_RAN=1
else
  echo "gate: none shipped (skipped)"
fi

fi
if [ "$GATES_REUSED" = "0" ] && [ "$GATES_RAN" = "1" ] && [ -n "$RECEIPT_TOOL" ] && [ -n "$ORIGIN_HEAD" ]; then
  python3 -B "$RECEIPT_TOOL" write "$SRC" --origin "$ORIGIN_HEAD" ${RC_ARGS[@]+"${RC_ARGS[@]}"} --seconds $(( $(date +%s) - GATE_T0 )) >/dev/null 2>&1 \
    && echo "package gates: receipt written ($(( $(date +%s) - GATE_T0 )) s)"
fi

# ---- 4. clone and BP-D7 guard ----
rm -rf "$TMP.repo"
git clone -q "$TARGET_URL" "$TMP.repo"
cd "$TMP.repo"
if [ -f "$PKG_DIR/VERSION.txt" ]; then
  PUB=$(tr -d ' \n\r' < "$PKG_DIR/VERSION.txt")
  NEWEST=$(printf '%s\n%s\n' "$PUB" "$VER" | sort -V | tail -1)
  [ "$VER" = "$PUB" ] && fail "v$VER is already published — a changed package needs a new version (BP-D7): raise VERSION.txt in the stage, then rewrite the manifest with oe_manifest"
  [ "$NEWEST" = "$VER" ] || fail "published v$PUB is newer than v$VER — refusing to move the package backwards"
  echo "supersedes published v$PUB"
fi
if git rev-parse -q --verify "refs/tags/${SLUG}-v${VER}" >/dev/null 2>&1; then
  fail "tag ${SLUG}-v${VER} already exists"
fi

# ---- 4b. CEREMONY, EXECUTED BY THE PUBLISHER (never trusted from an attestation) ----
# v1.8.2: a package published into the repository that holds its own governance cites it as "this
# repository" -- the commit hash still pins it exactly, and the distributable oe-method copy must not
# carry the account name its own clean gate forbids.
if [ "$GOV_REPO" = "$REPO" ]; then GOV_REPO_CITED="(this repository)"; else GOV_REPO_CITED="$GOV_REPO"; fi
# v1.8.1: measured, not assumed -- is the governance repository readable by others?
GOV_VIS=$(curl -s -H "Authorization: token ${TOKEN}" "https://api.github.com/repos/${GOV_REPO}" | python3 -c "import json,sys; print(json.load(sys.stdin).get('visibility','unknown'))" 2>/dev/null || echo unknown)
if [ "$GOV_VIS" = "public" ]; then
  GOV_NOTE="The governance repository is publicly readable; anyone can verify this citation directly."
else
  GOV_NOTE="Governance provenance here is a citation for the governance owner. The governance repository is ${GOV_VIS}, so readers of this repository are not expected to verify it, and no governing text is copied into it (owner ruling, 2026-09-24)."
fi
DISC=$(ls "$TMP.gov/$GOV_PATH"/04-documentation/OE_Operating_Discipline_v*.md 2>/dev/null | sort -V | tail -1)
[ -n "${DISC:-}" ] || fail "no OE Operating Discipline in $GOV_REPO/$GOV_PATH/04-documentation"
DSHA=$(sha256sum "$DISC" | cut -d" " -f1)
# v1.13.0: found by content in either layout (own file, or a module of the governance unit's A-Box), never by remembered path
RESOLVE=$(ls "$HERE"/oe_resolve_v*.py 2>/dev/null | grep -v _test_ | sort -V | tail -1)
if [ -n "${RESOLVE:-}" ]; then GSRCP=$(python3 -B -I "$RESOLVE" "$TMP.gov/$GOV_PATH" kb 2>/dev/null || true)
else GSRCP=$(ls "$TMP.gov/$GOV_PATH"/01-vocabularies/knowledge_base_abox_v*.ttl 2>/dev/null | sort -V | tail -1); fi
[ -n "${GSRCP:-}" ] || fail "no knowledge base found in $GOV_REPO/$GOV_PATH (own file or governance A-Box module) -- governance source unresolvable"
GSHA=$(sha256sum "$GSRCP" | cut -d" " -f1)
GSRC=$(basename "$GSRCP")
echo "governance: $GOV_REPO/$GOV_PATH @ ${GOV_COMMIT:0:7} (target: $REPO, package at ${PKG_DIR})"

# ---- 4a. FILE STRUCTURE AND NAMING (BP-D53), v1.11.0 ----
# CI Gate N already fails a push that adds a violation; this makes the publisher refuse first, before anything is pushed.
# The package is staged at its destination path and checked against the debt register the governance repository holds, so
# recorded debt passes and only a NEW violation refuses. A target without a register in governance is checked and reported,
# not refused (it has no recorded baseline to ratchet against). A scan of zero files is not a pass (exit 2).
STRUCT=$(ls "$HERE"/oe_structure_check_v*.py 2>/dev/null | grep -v _test_ | sort -V | tail -1)
if [ -n "${STRUCT:-}" ]; then
  # v1.14.0 (the owner's ruling of 2026-10-07): the governance package holds the AGGREGATE, which is the ceiling baseline,
  # and each package holds its own register. The checker (v1.4.0 and later) finds the staged package's own register by
  # itself and compares it with the aggregate, so there is nothing here to special-case: every package is treated alike,
  # where before only this one package's own register was read. The older aggregate name is still accepted for one
  # release, so a session publishing against a governance checkout from before the rename is not blocked.
  REGF=$(ls "$TMP.gov"/oe-pack/04-documentation/structure-debt/STRUCTURE_DEBT_AGGREGATE_v*.tsv 2>/dev/null | sort -V | tail -1 || true)
  if [ -z "${REGF:-}" ]; then
    REGF=$(ls "$TMP.gov"/oe-pack/04-documentation/structure-debt/STRUCTURE_DEBT_REGISTER_v*.tsv 2>/dev/null | sort -V | tail -1 || true)
  fi
  rm -rf "$TMP.struct"; mkdir -p "$TMP.struct"
  if [ "$PKG_DIR" = "." ]; then SPK="$SLUG"; else SPK="$PKG_DIR"; fi
  mkdir -p "$TMP.struct/$SPK"; (cd "$SRC" && tar --exclude=./.git -cf - .) | tar -xf - -C "$TMP.struct/$SPK"
  SARGS=(--package "${SPK%%/*}")
  [ -n "${OE_CLASSES_TABLE:-}" ] && SARGS+=(--classes "$OE_CLASSES_TABLE")
  [ -n "${REGF:-}" ] && SARGS+=(--register "$REGF")
  set +e; python3 "$STRUCT" "$TMP.struct" "${SARGS[@]}"; SRC_RC=$?; set -e
  rm -rf "$TMP.struct"
  if [ "$SRC_RC" != "0" ]; then
    if [ -n "${REGF:-}" ] || [ "$SRC_RC" = "2" ]; then
      fail "file structure and naming (BP-D53): a violation outside the debt register, or nothing examined — fix the files, do not edit the register to hide it; list the findings: python3 repo-tooling/oe_structure_check_v1_6_0.py <root> --list --package <name>"
    fi
    echo "  structure: violations reported; no governance register, so advisory only" >&2
  fi
else
  echo "  structure check not found in repo-tooling; skipped" >&2
fi
echo "discipline: $(basename "$DISC") sha ${DSHA:0:8}"
echo "governance source: $GSRC"

# ---- 4c. wholesale-replace guard (v1.5.5, stem-aware fix in v1.5.6) ----
# A real cross-session finding (a registrant package, 2026-09-09): step 5 clones origin
# fresh, then replaces $SLUG wholesale with $SRC, with no comparison of what origin's copy
# currently holds against what $SRC has. Any file origin gained under the package directory
# after $SRC was taken -- most commonly another session's own inbox filing -- is silently
# deleted, and the publish record reported PASS. Reproduced from the two commits the finding
# named before building this fix, not assumed from the report alone.
#
# v1.5.6: the first cut (plain file-list diff) flagged this session's OWN routine version bumps
# -- an old-versioned file $SRC has already renamed away from (e.g. foo_v1_0_0.ttl superseded by
# foo_v1_1_0.ttl) looks identical, from a bare diff, to a file another session added that this
# session never touched. Caught immediately on this publish's own dry run: it refused a normal
# version bump. Fixed with a stem match -- strip the trailing _v<version> token before comparing,
# so a file superseded by a newer version of itself in $SRC is recognised and not flagged; only a
# file whose STEM has no counterpart anywhere in $SRC is a genuine, unexplained addition.
#
# v1.5.7: v1.5.6's stem was directory-qualified, so a file MOVED between directories (the one
# thing every handover inbox does, disposing a proposal from pending/ to accepted/ or rejected/)
# read as a deletion of the pending/ copy and an unrelated new file at accepted/ -- refusing every
# publish that follows any package's own inbox disposition, ecosystem-wide. Caught by a real
# cross-session finding (a registrant package, 2026-09-10), reproduced directly before
# fixing: recognising a move requires matching on the version-stripped BASENAME alone, not the
# directory-qualified stem. The directory-qualified stem is kept for the report, so a genuine
# deletion is still named with its real path; only the match test changes.
DELETED_FILES=""
DELETED_COUNT=0
if [ -d "$PKG_DIR" ]; then
  DELETED_FILES=$(python3 <<PYSCRIPT
import os, re

def basename_stem(path):
    name = path.rsplit('/', 1)[-1]
    name = re.sub(r'[-_]v\d+(?:[._]\d+)*(\.\w+)\$', r'\1', name)
    return name

def file_list(root):
    out = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != '.git']
        for f in fn:
            out.append(os.path.relpath(os.path.join(dp, f), root))
    return out

origin_files = file_list("$PKG_DIR")
src_files = file_list("$SRC")
by_stem_src = {}
for f in src_files:
    by_stem_src.setdefault(basename_stem(f), []).append(os.path.dirname(f))
by_stem_org = {}
for f in sorted(origin_files):
    if os.path.basename(f) == "PUBLISH_RECORD.ttl":
        continue   # v1.8.0: regenerated by this publisher on every publish -- never a real deletion
    by_stem_org.setdefault(basename_stem(f), []).append(f)
def vkey(f):
    m = re.search(r'[-_]v(\d+(?:[._]\d+)*)\.\w+\$', f)
    return [int(x) for x in re.findall(r'\d+', m.group(1))] if m else []
src_set = set(src_files)
src_by_stem = {}
for f in src_files:
    src_by_stem.setdefault(basename_stem(f), []).append(f)
gone = []
for stem, files in by_stem_org.items():
    rest = [f for f in files if f not in src_set]                       # an exact path in the stage is kept, whatever its version
    free = [os.path.dirname(f) for f in src_by_stem.get(stem, []) if f not in set(files)]   # stage files of this stem that origin does not have yet
    rest.sort(key=vkey, reverse=True)                                   # the newest unmatched version is the one a stage file supersedes
    left = []
    for f in rest:
        d = os.path.dirname(f)
        if d in free:
            free.remove(d)
        else:
            left.append(f)
    for f in left:                                                      # leftovers pair with any free stage file (a move between folders); the rest have no partner
        if free:
            free.pop(0)
        else:
            gone.append(f)
for f in sorted(gone):
    print(f)
PYSCRIPT
)
  if [ -n "$DELETED_FILES" ]; then
    DELETED_COUNT=$(echo "$DELETED_FILES" | wc -l | tr -d ' ')
  fi
fi
if [ -n "$EXPECT_FILE" ]; then
  EXPECTED=$(grep -v '^[[:space:]]*\(#\|$\)' "$EXPECT_FILE" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sort -u || true)
  FOUND=$(printf '%s\n' "$DELETED_FILES" | grep -v '^$' | sort -u || true)
  NOT_DELETED=$(comm -23 <(printf '%s\n' "$EXPECTED" | grep -v '^$' || true) <(printf '%s\n' "$FOUND") || true)
  UNLISTED=$(comm -13 <(printf '%s\n' "$EXPECTED" | grep -v '^$' || true) <(printf '%s\n' "$FOUND") || true)
  if [ -n "$NOT_DELETED" ]; then
    echo "-- named-deletion guard: listed but not a deletion of this publish (typo, or already gone):" >&2
    echo "$NOT_DELETED" | sed 's/^/     /' >&2
    fail "named-deletion list names file(s) this publish does not delete — fix the list"
  fi
  if [ -n "$UNLISTED" ]; then
    echo "-- named-deletion guard: this publish would also delete, and the list does not name:" >&2
    echo "$UNLISTED" | sed 's/^/     /' >&2
    fail "publish would delete file(s) not named in $EXPECT_FILE (origin gained them after \$SRC was taken, or the list is incomplete) — refresh and re-list"
  fi
  echo "-- named-deletion guard: $DELETED_COUNT deletion(s), exactly the $(printf '%s\n' "$EXPECTED" | grep -vc '^$') listed — proceeding"
elif [ "$DELETED_COUNT" -gt 0 ]; then
  echo "-- wholesale-replace guard: $DELETED_COUNT file(s) exist at origin under ${PKG_DIR}/ with no counterpart (same basename) anywhere in \$SRC:"
  echo "$DELETED_FILES" | sed 's/^/     /'
  # v1.23.0: tell a file origin gained after its last release (not in origin's own latest manifest) from one the stage removed (listed there)
  OMF=$(ls "$PKG_DIR"/MANIFEST_SHA256*.txt 2>/dev/null | sort -V | tail -1 || true)
  if [ -n "$OMF" ]; then
    GAINED=$(printf '%s\n' "$DELETED_FILES" | while IFS= read -r f; do [ -n "$f" ] && ! grep -q -F -- "$f" "$OMF" && echo "$f"; done || true)
    if [ -n "$GAINED" ]; then
      echo "-- of these, origin's latest manifest does NOT list (filed after its last release -- most likely another session's handover; refresh the stage from origin before you name them):"
      echo "$GAINED" | sed 's/^/     /'
    fi
    echo "-- the others are listed by that manifest and absent from the stage: removed by the stage; name them with --expect-delete if each is meant"
  fi
  if [ "${FORCE:-}" != "--force" ]; then
    fail "publish would silently delete the $DELETED_COUNT file(s) above (origin gained them after \$SRC was taken) — if each one is meant to go, write the paths above (relative to the package, one per line) to a file and pass --expect-delete <file> (oe_release --deletions-file writes it); --force accepts every deletion unseen and is for emergencies"
  fi
  echo "WARNING: --force accepts EVERY deletion above, including any that arrived after you read the list; prefer --expect-delete <file> (L-126)" >&2
  echo "-- wholesale-replace guard: FORCE=--force set, proceeding — deletions recorded in the publish record"
fi

# ---- 4d. BP-D7 guard on names: a versioned file name is never reused for changed bytes ----
REWRITTEN=""
if [ -d "$PKG_DIR" ]; then
  REWRITTEN=$(python3 <<PYSCRIPT
import os, re
VER = re.compile(r'[-_]v\d+(?:[._]\d+)*\.\w+\$')
def files(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in ('.git', 'fixtures')]
        for f in fn:
            yield os.path.relpath(os.path.join(dp, f), root)
for rel in sorted(files("$SRC")):
    if not VER.search(os.path.basename(rel)): continue
    o = os.path.join("$PKG_DIR", rel)
    if os.path.isfile(o) and open(o, 'rb').read() != open(os.path.join("$SRC", rel), 'rb').read():
        print(rel)
PYSCRIPT
)
fi
if [ -n "$REWRITE_FILE" ]; then
  RW_EXPECTED=$(grep -v '^[[:space:]]*\(#\|$\)' "$REWRITE_FILE" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//' | sort -u || true)
  RW_FOUND=$(printf '%s\n' "$REWRITTEN" | grep -v '^$' | sort -u || true)
  RW_NOT=$(comm -23 <(printf '%s\n' "$RW_EXPECTED" | grep -v '^$' || true) <(printf '%s\n' "$RW_FOUND") || true)
  RW_EXTRA=$(comm -13 <(printf '%s\n' "$RW_EXPECTED" | grep -v '^$' || true) <(printf '%s\n' "$RW_FOUND") || true)
  [ -z "$RW_NOT" ] || { echo "$RW_NOT" | sed 's/^/     /' >&2; fail "rewrite list names file(s) this publish does not rewrite — fix the list"; }
  [ -z "$RW_EXTRA" ] || { echo "$RW_EXTRA" | sed 's/^/     /' >&2; fail "publish would also rewrite file(s) under an unchanged name that $REWRITE_FILE does not name (BP-D7)"; }
  echo "-- name guard (BP-D7): $(printf '%s\n' "$RW_FOUND" | grep -vc '^$') rewrite(s), exactly the listed ones — proceeding"
elif [ -n "$REWRITTEN" ]; then
  echo "-- name guard (BP-D7): file(s) that keep a versioned name with changed bytes:" >&2
  echo "$REWRITTEN" | sed 's/^/     /' >&2
  fail "a changed file gets a new version and the old one leaves (BP-D7): rename each file above to its next version (and the references to it); if a rewrite under the same name is truly meant, write the paths to a file and pass --expect-rewrite <file>"
fi

read -r TTL_TOTAL TTL_PARSED <<PYEOF
$(cd "$SRC" && python3 <<'PYSCRIPT'
import glob, os, rdflib
files = [f for f in glob.glob('**/*.ttl', recursive=True) if not {'fixtures', 'archive'} & set(f.split(os.sep)[:-1])]   # v1.10.2: same rule as step 2
total = len(files)
parsed = 0
for f in files:
    try:
        rdflib.Graph().parse(f)
        parsed += 1
    except Exception:
        pass
print(total, parsed)
PYSCRIPT
)
PYEOF
GATE_STATUS="NONE_SHIPPED"; [ -n "${GATE:-}" ] && GATE_STATUS="PASS"
if [ -f "$TMP.gate" ]; then cp "$TMP.gate" "$TMP.transcript"; else echo "no package gate shipped" > "$TMP.transcript"; fi
TSHA=$(sha256sum "$TMP.transcript" | cut -d" " -f1)
NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
VTOK=$(echo "$VER" | tr . _)

cat > "$TMP.record" <<TTLEOF
@prefix owl:     <http://www.w3.org/2002/07/owl#> .
@prefix xsd:     <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix prov:    <http://www.w3.org/ns/prov#> .
@prefix quality: <http://example.org/quality#> .
@prefix pub:     <http://example.org/publish-ceremony#> .
@prefix rel:     <http://example.org/reliability#> .
@prefix pkg:     <http://example.org/${SLUG}/publish#> .

pkg:Decision_v${VTOK} a quality:GateDecision , owl:NamedIndividual ;
    rdfs:label "Publish ceremony decision for ${SLUG} v${VER}"@en ;
    dcterms:identifier "${SLUG}"^^xsd:string ;
    owl:versionInfo "${VER}"^^xsd:string ;
    quality:passesGate true ;
    pub:disciplineSHA256 "${DSHA}"^^xsd:string ;
    pub:governanceSource "${GSRC}"^^xsd:string ;
    pub:governanceRepository "${GOV_REPO_CITED}"^^xsd:string ;
    pub:governanceFolder "${GOV_PATH}"^^xsd:string ;
    pub:governanceCommit "${GOV_COMMIT}"^^xsd:string ;
    pub:disciplineFile "$(basename "$DISC")"^^xsd:string ;
    pub:governanceSourceSHA256 "${GSHA}"^^xsd:string ;
    pub:packageLocation "${PKG_DIR}"^^xsd:string ;
    pub:governanceVisibility "${GOV_VIS}"^^xsd:string ;
    pub:governanceCitationNote "${GOV_NOTE}"@en ;
    pub:manifestVerified ${OK} ;
    pub:manifestTotal ${N} ;
    pub:turtleParsed ${TTL_PARSED} ;
    pub:turtleTotal ${TTL_TOTAL} ;
    pub:packageGate "${GATE_STATUS}"^^xsd:string ;
    pub:deletedFilesCount ${DELETED_COUNT} ;
    rel:authoringSession "${SESSION}"^^xsd:string ;
    quality:evidencedBy pkg:Evidence_v${VTOK} ;
    prov:generatedAtTime "${NOW}"^^xsd:dateTime .

pkg:Evidence_v${VTOK} a quality:Evidence , owl:NamedIndividual ;
    rdfs:label "Raw gate transcript for ${SLUG} v${VER}"@en ;
    pub:transcriptSHA256 "${TSHA}"^^xsd:string .
TTLEOF

VALIDATOR=$(ls "$HERE"/validate_publish_record_v*.py 2>/dev/null | sort -V | tail -1)
SHAPE=$(ls "$HERE"/publish_record_shacl_v*.ttl 2>/dev/null | sort -V | tail -1)
[ -n "${VALIDATOR:-}" ] && [ -n "${SHAPE:-}" ] || fail "ceremony validator or shape not found in repo-tooling/"
echo "shape: $(basename "$SHAPE")"
python3 "$VALIDATOR" "$TMP.record" "$SHAPE" \
  || fail "publish record is non-conformant against the ceremony shape"

if [ "$DRY" = "--dry-run" ]; then
  echo "DRY RUN — every check passed and the record conforms; nothing pushed"
  rm -rf "$TMP.repo" "$TMP.mf" "$TMP.gate" "$TMP.record" "$TMP.transcript"; exit 0
fi

# ---- 5. publish ----
git remote set-url origin "${OE_TARGET_URL:-https://github.com/${REPO}.git}" 2>/dev/null || true
echo "token scrubbed: $(grep -c 'x-access-token' .git/config 2>/dev/null || echo 0) refs in .git/config"
git remote set-url origin "$TARGET_URL"   # v1.8.0: was hard-coded to github.com, ignoring the target URL
git config user.name "${OE_GIT_NAME:-the method author}"
git config user.email "${OE_GIT_EMAIL:-yusuf@altunel.dev}"
if [ "$PKG_DIR" = "." ]; then   # v1.8.0 package-at-root: replace everything except the target's own .git
  find . -mindepth 1 -maxdepth 1 ! -name .git -exec rm -rf {} +
  (cd "$SRC" && tar --exclude=./.git -cf - .) | tar -xf -
else
  rm -rf "$PKG_DIR"; mkdir -p "$PKG_DIR"   # v1.10.0: the destination is PKG_DIR, which is $SLUG only by default
  cp -r "$SRC/." "$PKG_DIR/"
fi
[ "$PKG_DIR" = "." ] || rm -rf "$PKG_DIR/.git"  # BP-D7 PATCH v1.5.1: SRC is often a git clone (a session's working tree);
                     # copying its .git created an embedded-repo GITLINK in the destination
                     # (mode 160000, not 040000) — the published subfolder looked committed but
                     # was empty on any fresh clone. Caught on oe-method v2.8.0's first real
                     # publish (dry-run cannot catch this: it never writes the tree).
[ "$PKG_DIR" = "." ] || git rm -r --cached "$PKG_DIR" -q 2>/dev/null || true
                     # BP-D7 PATCH v1.5.2: v1.5.1's fix alone was insufficient. A path git has
                     # ALREADY committed as a gitlink is treated as submodule-managed — `git add
                     # -A` / `git status` silently ignore its on-disk contents entirely, even
                     # after real files replace it, because there is no .gitmodules declaring it.
                     # v2.8.1's first attempt under v1.5.1 reported "nothing to commit, working
                     # tree clean" with real files sitting right there — verified by manually
                     # reproducing the copy in a scratch clone and finding `git status` reported
                     # zero changes until the stale index entry was removed with `git rm --cached`
                     # first. Harmless no-op the first time SLUG is published (nothing cached yet).
find "$PKG_DIR" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
find "$PKG_DIR" \( -name '*.pyc' -o -name '*.pyo' \) -delete 2>/dev/null || true
cp "$TMP.record" "$PKG_DIR/PUBLISH_RECORD.ttl"
git add -A
USAGE_ARGS=()
USAGE_TOOL=$(ls "$HERE"/oe_session_usage_v*.py 2>/dev/null | sort -V | tail -1)
if [ -n "$USAGE_TOOL" ]; then
  USAGE_LINE=$(OE_SESSION="$SESSION" python3 "$USAGE_TOOL" --trailer 2>/dev/null) || USAGE_LINE=""
  case "$USAGE_LINE" in
    Session-Usage:*) USAGE_ARGS=(-m "$USAGE_LINE"); echo "usage recorded: $USAGE_LINE" ;;
    *) echo "note: session usage not measurable here; publish commit carries no Session-Usage trailer" ;;
  esac
fi
git commit -q -m "$SLUG v$VER" -m "Session: ${SESSION}" -m "Ceremony executed by the publisher, not attested: discipline ${DSHA:0:8}, governance source $GSRC, manifest $OK/$N, Turtle $TTL_PARSED/$TTL_TOTAL, package gate $GATE_STATUS. PUBLISH_RECORD.ttl conforms to $(basename "$SHAPE")." "${USAGE_ARGS[@]}"
git tag -a "${SLUG}-v${VER}" -m "$SLUG v$VER"
git push -q origin main
TAG_STATE="tag ${SLUG}-v${VER}"
git push -q origin "${SLUG}-v${VER}" || { TAG_STATE="tag ${SLUG}-v${VER} left to the workflow"; echo "TAG NOTICE: ${SLUG} v${VER} is published (commit $(git rev-parse --short HEAD)); the tag ${SLUG}-v${VER} was not pushed from here, which is expected. A session's git proxy refuses tag pushes (measured 2026-10-05: HTTP 403 on the push leg, while the branch push to the same repository succeeded). The commit is the release; the tag is only its label, and the label is made on GitHub's side by the 'OE tags' workflow (.github/workflows/oe-tags.yml) on the push that just happened. Do not push the tag from a session and do not look for another route: check the remote instead, after the workflow has run -- git ls-remote --tags origin | grep ${SLUG}-v${VER}. If that comes back empty, this repository has not adopted the workflow; ask the owner to add it (the current version is adapted to the layout of the repository it runs in) rather than pushing the tag by hand." >&2; }
echo "published: $SLUG v$VER  (${TAG_STATE}, commit $(git rev-parse --short HEAD))"
rm -rf "$TMP.repo" "$TMP.gov" "$TMP.mf" "$TMP.gate"

# ---- 6. mirror (v1.7.0) ----
# The standalone oe-method repository mirrors the monorepo's oe-method/ folder. After publishing
# that package, sync the mirror in the same run; if the sync cannot complete, open (or refresh) an
# issue on the source repository so the need is visible -- the publish itself already succeeded
# and is never rolled back for a mirror failure.
if [ "$SLUG" = "${OE_MIRROR_FOR:-oe-method}" ]; then
  cd "$HERE"   # v1.7.1: the temp clone (our cwd) was just deleted above; git and python both fail in a deleted cwd
  if bash "$HERE/oe_mirror_sync_v1_0_0.sh" "$TOKEN"; then :; else
    echo "MIRROR NOTICE: $SLUG v$VER published, but its mirror could not be updated automatically." >&2
    python3 - "$TOKEN" "$REPO" "$SLUG" "$VER" <<'PYEOF' || echo "MIRROR NOTICE: could not open an issue either -- update the mirror by hand." >&2
import json, sys, urllib.request
tok, repo, slug, ver = sys.argv[1:5]
title = f"{slug} mirror update needed"
body = (f"`{slug}` v{ver} was published to `{repo}`, but the mirror could not be updated automatically.\n\n"
        f"Run `bash repo-tooling/oe_mirror_sync_v1_0_0.sh <token>` from a session, then close this issue.")
h = {"Authorization": f"token {tok}", "Accept": "application/vnd.github+json"}
q = urllib.request.Request(f"https://api.github.com/repos/{repo}/issues?state=open&per_page=100", headers=h)
existing = [i for i in json.load(urllib.request.urlopen(q)) if i["title"] == title]
if existing:
    url, data, method = f"https://api.github.com/repos/{repo}/issues/{existing[0]['number']}/comments", {"body": body}, "POST"
else:
    url, data, method = f"https://api.github.com/repos/{repo}/issues", {"title": title, "body": body}, "POST"
urllib.request.urlopen(urllib.request.Request(url, data=json.dumps(data).encode(), headers=h, method=method))
print("MIRROR NOTICE: issue opened/updated on", repo)
PYEOF
  fi
fi
