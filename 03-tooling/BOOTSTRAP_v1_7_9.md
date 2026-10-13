# Parallel-session bootstrap v1.7.8

**One block. Identical for every session.** The operator fills the token once and pastes the same
text everywhere — the session works out its own package, resolves the current discipline by
version, and checks it is not working from a stale copy.

New in v1.7.8: **the ceremony (v1.0.5) counts the inbox correctly.** The line "handover inbox pending" counted the OE pack's pending folder with its README and said so for every package, so a package whose own inbox was empty read "2 item(s)". It now prints the OE inbox (README not counted) and, for any other package, that package's own inbox on a line of its own. Nothing else changed.

New in v1.7.7: **the ceremony (v1.0.4) reads the governance aggregate as the structure-debt baseline** (the owner's ruling of 2026-10-07: each package carries its own register). Stage 6 of v1.0.3 still took the governance package's register by its old name, which is now that package's own two-line register, so every session's ceremony ended "FAIL -- a package's own register tried to widen what the governance aggregate records". Nothing else changed.

New in v1.7.6: **the knowledge base is resolved by content, not by remembered path.** After the package consolidation (BP-D54) it may be a module inside the governance unit's A-Box, so STEP 4 runs `python3 -I repo-tooling/oe_resolve_v1_0_0.py oe-method kb`, which prints the highest-version A-Box that holds lessons or best practices (own file or module) and refuses (exit 2) when none does. The publisher (v1.13.0) and the digest (v1.1.0) use the same resolver.

New in v1.7.5: **the file-structure unit is the package** (owner's ruling of 2026-10-06, BP-D54): one T-Box, one A-Box and one SHACL file in all, each with one ontology header and one version; former subjects become modules inside; the archive is one triad. `oe_structure_check_v1_1_0.py` reports N1, N2, V1, R1, H1 (several headers in a file), U1 (several active files of a role in a package) and A1 (the same for the archive); a package is the nearest folder holding a `VERSION.txt`. Stage 6 of the ceremony and the publisher use it; it still informs in the ceremony and refuses in the publisher and in CI. The paragraph below (v1.7.3) speaks of one triad per subject; read it with this one.

New in v1.7.4: **the ceremony (v1.0.3) no longer refuses when another session files a handover into the inbox** (`07-handover-inbox/pending/`): the filing session cannot update this package's manifest, so an arrival used to read as a stowaway. A file listed in the manifest is still hash-checked; any other unlisted file still refuses.

New in v1.7.3: **the ceremony reports the package's file-structure and naming debt** (stage 6, BP-D53: one T-Box, one A-Box and one SHACL file per subject, no mixed or patch files, one current version per file). It informs and does not refuse; `oe_structure_check_v1_0_0.py` runs on every push in CI and fails on any violation not in the dated debt register (`oe-pack/04-documentation/structure-debt/`). Clear your own package's lines, then delete them from the register.

New in v1.7.2: **the discipline is read as a digest.** `oe_ceremony_digest_v1_1_0.py` prints every rule section in full and the change history as headings, and checks that the two rules that used to live only in the history are in the rule sections now (discipline v2.13.1+); about a third fewer tokens per ceremony, and `--full` still prints everything. The alarm thresholds are now judged against the session's own floor (consider at floor + 100,000, hand over at floor + 150,000).

New in v1.7.0: **the ceremony is one command, and it refuses.** The order B5 prescribes — access,
freshness, discipline version, counts, manifest — was carried here as prose across STEP 2/3/4, so
each session executed its own arrangement of it and reported its own selection of numbers.
`oe_ceremony_v1_0_6.sh` runs the whole order and prints one verdict, `PROCEED` or `REFUSE`. It is
strictly stronger than the prose it replaces, not a shortcut through it: the governing discipline is
resolved by highest SemVer **on GitHub as well as on disk** and the local bytes are compared with
the remote blob through the authenticated API, so a local copy that differs from the repository, or
a repository version higher than the local one, refuses; a stale checkout refuses rather than
warns; and the manifest check is the stowaway-aware verifier, not the listed-files-only
`sha256sum -c` idiom. Reading the local file and reporting its digest — what STEP 4 asked for —
proves the snapshot is undamaged and nothing about whether it is the repository's current text,
which is the same internal-consistency gap B5 was enriched to close, one level up. Proven in both
directions before it was adopted: a tampered discipline, a checkout one commit behind, a stowaway
in the package and an unreadable API each refuse; the clean tree proceeds.

New in v1.6.0: **a measuring step, a handover alarm, a usage record, and an upload rule.** Sessions
now report what they spent from the recorded numbers, not from impression (STEP 6); every turn's
freshness check prints a one-line alarm saying whether to hand over (STEP 2); the usage measured at
handover is recorded as a `Session-Usage:` trailer on the handover commit, from which daily and weekly
summaries are computed (STEP 6), and material that arrives as a package is verified
after unpacking, because the bytes inside govern, not the wrapper. The reasons are in
`SESSION_OPTIMIZATION`: usage is recorded per message and repeated on every record of that message,
so the tool counts each message once; the attached v1.3.0 file carried 49 escaped underscores that
no wrapper would have removed.

New in v1.3.0: **`OE_SESSION`**. Several sessions write to one governed store under one configured
git author — measured: 125 of 134 commits carried the same author identity, so the record said what
changed and never which session changed it. That is what makes `ParallelSessionLineageFork` and
`CrossSessionContamination`, both named in the pack's own reliability vocabulary, undiagnosable.
The publisher now writes `$OE_SESSION` into `PUBLISH_RECORD.ttl` and into a `Session:` git trailer.
It is attribution, not authentication: a session declares its own name, an absent declaration is
recorded as `unattributed` and warned about, never inferred from the git author.

Carried from v1.2.0, both from real failures rather than tidiness:

- **A freshness step.** B5 was enriched at pack v20.30.0 after a session reported that
  SHA-verifying against the internal manifest is an internal-consistency check — it proves a
  snapshot is undamaged and is equally true of one six months stale. On its first use the new step
  found this session four commits behind origin, with a parallel session's work already pushed.
- **Explicit discipline resolution.** The discipline filename carries its version, so any fixed
  path or URL goes stale on the next bump — `v2_2_0` → `v2_3_0` happened mid-programme. Resolve by
  highest SemVer, never by a remembered name.

---

```
export GH_PAT=<your-token>
export OE_SESSION=<short-name-for-this-session>   # e.g. brsf-session, lcwkb-session

You own an ontology package in the OE ecosystem. Work under strict OE discipline.

STEP 0 — work out what you own, do not ask me to edit this prompt
  If OE_SESSION is unset, pick a short stable name for yourself, export it, and say what you
  chose. Do not proceed unattributed: an unattributed change is recorded as such permanently.
  SLUG   = the package you have been working on in this session, as a lowercase slug
  PKGDIR = the absolute path to its source directory on this container
  It must contain VERSION.txt and a MANIFEST_SHA256*.txt that self-verifies.
  State both in one line and continue. Ask me only if you genuinely cannot determine them.

STEP 1 — set up and clone once
  pip install rdflib pyshacl --break-system-packages -q
  cd /home/claude
  git clone https://x-access-token:$GH_PAT@github.com/your-account/Ontologies.git
  cd Ontologies
  git remote set-url origin https://github.com/your-account/Ontologies.git
  chmod +x repo-tooling/*.sh repo-tooling/*.py

STEP 2 — THE CEREMONY, before anything else (B5, pack v20.30.0)
  bash "$(ls repo-tooling/oe_ceremony_v*.sh | sort -V | tail -1)" "$SLUG"
  One command, the same order in every session: access, freshness against origin, the governing
  discipline resolved by version and compared byte-for-byte with the repository through the
  authenticated API, counts, and the stowaway-aware manifest check. It ends in PROCEED or REFUSE
  and exits non-zero on REFUSE. On REFUSE, clear the named line and run it again; do not proceed
  and do not work around it. Report its last line verbatim in your first message, so a stale
  resolution or a drifted local copy is visible immediately.
  Run the freshness part again before every write — a parallel session may have pushed while you
  worked; re-running the whole command is cheap (measured 2026-10-05: 3.9 s on a fresh clone).
  If the ceremony script is missing, the order it runs is still the order; the steps by hand are:
  git -c credential.helper= fetch https://x-access-token:$GH_PAT@github.com/your-account/Ontologies.git main
  git rev-list --left-right --count HEAD...FETCH_HEAD
  The right-hand number must be 0. If it is not, you are working from a stale copy:
  git pull --rebase, then re-check. A manifest that verifies N/N tells you the snapshot is
  undamaged; it tells you nothing about whether it is current, and a digest you read off your own
  disk tells you nothing about whether it matches the repository.
  Then, every turn, one line — the handover alarm (advisory; OK / CONSIDER-HANDOVER / HANDOVER):
    python3 "$(ls repo-tooling/oe_session_usage_v*.py | sort -V | tail -1)" --brief
  The line is a signal, not the decision. On CONSIDER-HANDOVER or HANDOVER run the decision (advisory):
    python3 "$(ls repo-tooling/oe_session_usage_v*.py | sort -V | tail -1)" --decide --horizon <messages of work ahead>
  It weighs cost, prediction, risk, history and impact together and holds only if it holds under the
  parameters a session cannot measure. FINISH-FIRST: commit and push, then decide again. SWITCH: hand
  over at the next clean stopping point. STAY-UNLESS-LONG: it states the break-even in messages.
  STAY: carry on. (Method, evidence and limits: SESSION_OPTIMIZATION, section 9; thresholds: section 5.)

STEP 2b — A GATE THAT FINDS NOTHING MUST FAIL, NEVER PASS
  Before trusting any gate you inherit, check what it actually examined. A gate that hard-codes a
  path reports "0/0 OK" or "no X found" in a package whose layout differs — passing, or failing
  quietly, on an empty set. This concealed four SHACL violations in the governing pack itself for
  an unknown period, and took four turns to diagnose because each patched path exposed the next.
    bash/python your release gate and read the COUNTS, not the verdict.
    Any line reading 0/0, "none shipped", or "no X found" means that check never ran.
  Use release_check_v2_0_0.py, which discovers manifest, ontologies and shape suites by content and
  treats an empty discovery as a failure. If you write a gate, apply the same rule to it: report
  what was examined, and refuse when that is nothing. An absence of evidence reported as evidence
  of absence is the decorative-verification failure, committed by the instrument.

STEP 3 — verify the tooling before running it (BP-D2)
  cd repo-tooling
  MF=$(ls MANIFEST_SHA256_v*.txt | sort -V | tail -1)
  grep -v '^#' "$MF" | grep . | sed -E 's/[[:space:]]+\([0-9]+b\)[[:space:]]*$//' | sha256sum -c
  cd ..
  Every line must report OK. If any does not, STOP and report it.

STEP 4 — resolve the governing artifacts BY VERSION, never by remembered name
  DISC=$(ls oe-method/04-documentation/OE_Operating_Discipline_v*.md | sort -V | tail -1)
  GSRC=$(python3 -I repo-tooling/oe_resolve_v1_0_0.py oe-method kb)   # exit 2 = REFUSED: stop and report
  PROMPT=$(ls repo-tooling/SESSION_PROMPT_v*.md                    | sort -V | tail -1)
  Report the basename and SHA-256 of $DISC in your first message, so a stale resolution is
  visible immediately. Read $DISC through the digest, not whole: `python3 repo-tooling/oe_ceremony_digest_v1_1_0.py .`
  (rule sections in full, change history as headings, lessons cited only in the history with their
  labels). It must print `RULES CHECK: OK`; if it prints FAIL or exits non-zero, read $DISC whole
  (`--full`). Read the full history when a question turns on why a version changed. Read $PROMPT and follow
  both for the rest of the session.
  Resolve EVERY governed file this way. Filenames carry version tokens (BP-D6); a path you
  remember from a previous session names a version that may now be retired.

STEP 5 — publish
  PUB=$(ls repo-tooling/oe_publish_v*.sh | sort -V | tail -1)
  bash "$PUB" "$GH_PAT" "$PKGDIR" "$SLUG" --dry-run
  bash "$PUB" "$GH_PAT" "$PKGDIR" "$SLUG"

  The publisher records $OE_SESSION as reliability:authoringSession in PUBLISH_RECORD.ttl and as a
  Session: git trailer, and (v1.9.0+) ends its commit with the session's Session-Usage: trailer. It warns and records 'unattributed' if OE_SESSION is unset.
  To see who has been changing what:
    python3 repo-tooling/oe_session_register_v*.py --repo-root .

  The publisher re-executes the ceremony itself, emits $SLUG/PUBLISH_RECORD.ttl, SHACL-validates
  it, then commits and pushes the branch. It refuses on any failing check or an already-published
  version (BP-D7) — fix the artifact, not the report.

  It does NOT push the release tag, and neither do you. A session's git proxy refuses tag pushes
  (measured 2026-10-05: HTTP 403 on the push leg; the branch push to the same repository succeeds,
  and `git push --dry-run` reports success, so the dry run is not evidence). The commit is the
  release; the tag $SLUG-vX.Y.Z is only its label, and the label is made on GitHub's side by the
  "OE tags" workflow (.github/workflows/oe-tags.yml) on the push that just happened. The publisher
  prints a TAG NOTICE saying so; that notice is the expected outcome, not a failure. Confirm it
  instead of acting on it:
    git ls-remote --tags origin | grep "$SLUG-v"
  Empty means the repository has not adopted the workflow — ask the owner to add it, adapted to
  that repository's layout and existing tag prefix, rather than pushing the tag by hand.

  If the push is rejected as non-fast-forward, another session published first: that is STEP 2's
  failure mode arriving late. git pull --rebase and re-run. Never force-push (L-112).

STEP 6 — MEASURE (at every handover, at session close, and whenever asked)
  python3 "$(ls repo-tooling/oe_session_usage_v*.py | sort -V | tail -1)"
  Report from its output only: tokens by model, human turns, context re-read per turn, the largest
  tool results, and the work done before the first file edit. If it refuses, say so; never fill the
  gap with an estimate. The request to give any session, and the model-fit table, are in
  repo-tooling/SESSION_OPTIMIZATION_v*.md (highest version).
  Record it on the handover commit. A publish does this for you; for a handover commit you make
  yourself, append the trailer as the message's LAST paragraph:
    U=$(python3 "$(ls repo-tooling/oe_session_usage_v*.py | sort -V | tail -1)" --trailer)
    git commit -m "<subject>" -m "<body>" -m "$U"
  One record per handover, never per turn. Summaries, any time:
    python3 "$(ls repo-tooling/oe_session_usage_v*.py | sort -V | tail -1)" --summarise --repo-root . --by day|week|session

UPLOADS
  Material that arrives as a .zip: unpack it, then verify the inner manifest. The wrapper's own
  digest proves nothing about the files. Read headings and slices, never a whole file over 200 KB.
  The token is exported from the environment and is never written into a file that is attached,
  committed, or pasted.

REPORT
  Executed results with numbers. No preamble.
```

---

## Fetching the current discipline without a clone

Where a session only needs the discipline and not the whole repository — a reviewer, or a check
from another machine — the directory is stable and the filename is not:

```bash
API=https://api.github.com/repos/your-account/Ontologies/contents/oe-method/04-documentation
NAME=$(curl -sS -H "Authorization: Bearer $GH_PAT" -H "Accept: application/vnd.github+json" "$API" \
  | python3 -c "import json,sys,re; c=[x['name'] for x in json.load(sys.stdin) if re.match(r'OE_Operating_Discipline_v\d+_\d+_\d+\.md$',x['name'])]; c.sort(key=lambda n:[int(i) for i in re.findall(r'\d+',n)]); print(c[-1])")
curl -sS -H "Authorization: Bearer $GH_PAT" -H "Accept: application/vnd.github.raw" "$API/$NAME" -o "$NAME"
```

The sort is numeric, not lexicographic: plain `sort` puts `v2_10_0` before `v2_9_0` and would
hand back a retired version. No pointer file or fixed-path copy is used deliberately — a second
copy at a stable path is a second lineage, and lineages drift.

## Already published

`oe-pack` · `repo-tooling` · `a domain ecosystem` · `a registrant package` · `a teaching tool` ·
`semtech-landscape` · `semtech-ecosystem` · `agentic-systems` · `lcw-principles-kb`

Any other slug creates its package directory on first publish.
