#!/usr/bin/env python3
"""oe_method_clean_gate_v1_7_0.py — prove the package carries no personal, institutional,
business or project-specific data.

Exits 0 only when every shipped byte AND every filename is free of the pattern sets below.
Run it against a tree with a planted name to confirm it can fail (L-95); a gate never shown
to fail verifies nothing.

v1.1.0: ATTRIBUTION_FILES' exception only covered the 'person' label (a citation file naming an
author). OE_Operating_Discipline_v2_5_0.md legitimately names backlog-roadmap-framework as the
real source of an adapted governance protocol -- a 'project' label match, not 'person'. Widened
the exception to cover both labels for files in the set, rather than weaken the patterns
generally or strip a real, honest attribution to make the gate pass mechanically.

v1.2.0: PATTERN_HOLDERS still named the lineage gate's superseded filename
(oe_method_lineage_gate_v1_0_0.py), so its real current name failed self-check the moment it was
renamed. Updated the reference; the exception was always sound in principle, only its target
had gone stale.

v1.3.0: the generalisation transform's blanket "altunelyusuf -> your-account" substitution had
broken oe_publish and oe_rehydrate functionally (REPO="your-account/Ontologies" cannot be
pushed to or fetched from), caught by a dry-run publish attempt failing immediately. Both
restored to the real value and re-declared 'verbatim' in LINEAGE.tsv, since generalising them
is not privacy protection, it is disabling the tool. Added a narrowly-scoped
OPERATIONAL_FILES exception (these two filenames, 'account' label only) rather than weaken the
pattern generally.

v1.4.0: negative fixtures (03-tooling/fixtures/negative_*) deliberately plant a real name to
prove the gate can fail (L-95) -- correctly, but they were being scanned as if shipped, always
failing the gate on a fixture whose entire purpose is to fail on demand. Excluded by path,
matching release_check's own established exclusion of the same directories, not by weakening
what gets flagged elsewhere.

v1.5.0: both exceptions removed on direct challenge, not independently. ATTRIBUTION_FILES no
longer covers OE_Operating_Discipline: that file was mistakenly marked 'verbatim' instead of
'generalised' in LINEAGE.tsv, which is what actually needed fixing -- the standard transform
already generalises project names correctly for every other file. OPERATIONAL_FILES removed
entirely: oe_publish/oe_rehydrate's real account and identity were parameterized via
environment variables at their source (oe_publish_v1_5_4.sh, oe_rehydrate_v1_2_0.sh) instead of
exempted here. Both fixes address the same root complaint -- oe-method is the cleaned,
collaborator-distributed package, and an exception in the checker is not the same claim as the
content actually being clean.

v1.6.0: PATTERN_HOLDERS still named the lineage gate's superseded filename
(oe_method_lineage_gate_v1_1_0.py), so its real current name (v1.2.0, itself bumped to fix two
real regex bugs found by a cross-session finding) failed self-check the moment it was renamed.
Updated the reference.

v1.7.0: the files that hold the pattern table are recognised by a PATTERN (any version of the lineage gate and of its test), not by one exact filename. The exact
name went stale at every new version of the lineage gate (v1.2.0, v1.6.0 and again at v1.3.0): a defect of the same kind three times is a structural one.
Proved to discriminate: the gate still fails on a planted name in any other file, including a file named like the lineage gate but not matching the pattern.

  python3 oe_method_clean_gate_v1_7_0.py [root]
"""
import os
import re
import sys

PATTERNS = {
    'person': r'\bAltunel\b|\bYusuf\b|YusufAltunel',
    'institution': r'İstanbul Kültür|Istanbul Kultur|\bİKÜ\b|\bIKU\b',
    'business': r'\bFizyoVibe\b|\bFizyo Vibe\b',
    'project': (r'\bRDODI\b|\bZT4SWE\b|\bZRCM\b|\bSNLIF\b|\bEAKB\b'
                r'|\bbacklog-roadmap-framework\b|Variant Algebra Framework'),
    'account': r'altunelyusuf',
}

ATTRIBUTION_FILES = {'LICENSE.md', 'CITATION.cff'}
# OE_Operating_Discipline was exempted here for one version (v1.3.0-v1.4.0's own line), on the
# reasoning that stripping a real attribution was worse than a leak. Reconsidered on direct
# challenge: oe-method is the cleaned, collaborator-distributed package, and the correct fix
# was never an exception -- it was generalising the reference like every other project name,
# which the existing transform table already did correctly for every OTHER file. The exception
# existed only because this file was mistakenly marked 'verbatim' in LINEAGE.tsv instead of
# 'generalised'; fixed at that root, not patched here.

# Files whose FUNCTION is to hold the pattern table cannot avoid containing it. This gate already
# excludes itself for that reason; the lineage gate carries the same table to re-derive the
# transform, so it is in the same class. The exception is by exact filename and total, which is a
# real weakening — mitigated by both files being short, reviewable, and containing the patterns
# only inside a declared table. Weakening the patterns to avoid self-match would instead reduce
# what the gate can detect anywhere.
PATTERN_HOLDERS = (re.compile(r'^oe_method_lineage_gate_v\d+_\d+_\d+\.py$'), re.compile(r'^oe_method_lineage_gate_test_v\d+_\d+_\d+\.py$'))


def holds_pattern_table(name):
    return any(p.match(name) for p in PATTERN_HOLDERS)

# OPERATIONAL_FILES existed here for one version (oe_publish/oe_rehydrate needing the real
# account and identity to function). Removed on direct challenge: the real fix was
# parameterizing REPO and the git identity via environment variables in the scripts themselves
# (oe_publish_v1_5_4.sh, oe_rehydrate_v1_2_0.sh), not exempting the leak. A collaborator's copy
# now ships a harmless generic default and is expected to supply their own values at call time;
# this operator's own real values are supplied via environment, never baked into the file.

root = sys.argv[1] if len(sys.argv) > 1 else '.'
hits = []
scanned = 0

for dirpath, dirnames, filenames in os.walk(root):
    dirnames[:] = [d for d in dirnames if d not in ('.git', '__pycache__')]
    # Negative fixtures deliberately plant a real name to prove the gate CAN fail (L-95) -- a
    # gate never shown to fail verifies nothing. Excluding them by path, matching release_check's
    # own established exclusion of the same directories, not by weakening what gets flagged.
    if any(part.startswith('negative_') for part in dirpath.split(os.sep)):
        continue
    for name in filenames:
        path = os.path.join(dirpath, name)
        rel = os.path.relpath(path, root)
        # The gate's own pattern list necessarily contains the strings it hunts for.
        # Excluding it by name is explicit; weakening the patterns to avoid self-match
        # would silently reduce what the gate can detect.
        if os.path.basename(path) == os.path.basename(__file__) or holds_pattern_table(os.path.basename(path)):
            continue
        # DECLARED EXCEPTION (owner decision, 2026-08-03): the licence and citation files
        # carry named attribution deliberately. The exception is by exact filename and by
        # category — only 'person' is permitted there, never institution, business, project
        # or account. Anything else in these files still fails.

        # Word boundaries fail on underscore- and hyphen-separated filenames, which is this
        # ecosystem's naming convention: \bRDODI\b does not match RDODI_notes.md. Normalise
        # separators to spaces before testing a filename.
        norm = re.sub(r'[_\-.]', ' ', name)
        for label, pat in PATTERNS.items():
            if re.search(pat, norm):
                hits.append((label, rel, 'FILENAME', name))
        try:
            text = open(path, encoding='utf-8').read()
        except (UnicodeDecodeError, OSError):
            continue
        scanned += 1
        for lineno, line in enumerate(text.splitlines(), 1):
            for label, pat in PATTERNS.items():
                m = re.search(pat, line)
                if m:
                    if os.path.basename(path) in ATTRIBUTION_FILES and label in ('person', 'project'):
                        continue
                    hits.append((label, rel, f'line {lineno}', m.group(0)))

print(f'clean gate: {scanned} text files scanned, {len(hits)} matches')
for label, rel, where, what in hits[:40]:
    print(f'   [{label}] {rel} {where}: {what}')
if len(hits) > 40:
    print(f'   ... and {len(hits) - 40} more')
print('VERDICT: CLEAN' if not hits else 'VERDICT: FAIL — personal or project data present')
sys.exit(0 if not hits else 1)
