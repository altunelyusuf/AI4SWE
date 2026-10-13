# OE Operating Discipline — v2.17.1 (generalised variant of v2.17.0)

**Governance source:** the latest OE ABox — the highest-versioned `01-ontologies/knowledge_base_abox_v*.ttl` (SemVer order) in the attached OE Pack. Attach the OE Pack with every request that uses this discipline.

## Pointer resolution — version-independent (v2.2.0)

All artifact references in this discipline are **patterns, not pinned filenames**:
- Wherever an artifact is named, resolve to the **highest-versioned** matching `name_v*.<ext>` in the attached OE Pack (SemVer order). `MANIFEST_SHA256.txt` is authoritative for what ships.
- This applies to the discipline itself: the governing copy is the highest-versioned `04-documentation/OE_Operating_Discipline_v*.md` **inside the attached pack**. A detached copy of this file is **non-authoritative** the moment it diverges from the in-pack copy (BP-D2: pack bytes govern).
- Validators are invoked the same way (e.g. the highest `03-tooling/release_check_v*.sh`), and every gate a validator claims must run **self-contained against the attached pack** — no chaining to scripts the pack does not ship (L-34).
- Consequence: KB/tooling version bumps never require editing this file again. Any future edit that DOES change this file's text must bump its version (BP-D7) — **global repoint scripts must exclude this file**.

---

## The ceremony — execute before ANY substantive action (non-negotiable)

1. **List** the specific BP/L IDs that govern the action, each with a one-line reason.
2. **Extract** their verbatim `skos:definition` **programmatically** from the latest OE ABox (rdflib) and paste it. Never reconstruct from memory or from this file. Standing rule: verbatim `skos:definition` is always extracted programmatically from the latest OE ABox; **BP-D39 never overrides this**.
3. **State** what enforcement looks like on this specific action.

If you cannot complete steps 1–3, **STOP and ask**. Any "do X before Y" with X skipped is a **FAIL-STOP**, not a hedge.

---

## Eight standing boundaries the ceremony does not structurally reach

These are the failure modes observed in practice that the three-step ceremony, run correctly, still does not catch on its own. They are governed by lessons in the OE ABox; step (2) will surface their verbatim text when they apply. They are restated here because each is a boundary about *something other than within-artifact correctness*, which is all the ceremony checks.

### B1 — Cross-session scope / contamination (L-64)
If the verification target or subject of a request is an artifact **owned by another session** (e.g. a parallel session's corpus), the deliverable is a **PROPOSAL, not an edit**. A ruling on a *decision* (e.g. "Branch B is correct") is **not** authorization to mutate files outside this session's ownership. Produce the findings + exact fixes + verification method for the owning session to apply; if a worked copy helps, ship it explicitly labelled `REFERENCE_ONLY … NOT_A_RELEASE`. Tell: you are about to edit, version-bump, or repackage a file this session did not author. Stop — propose instead.

### B2b — Derivable versus stipulated decisions, inside your own package (L-116)
B1 governs artifacts another session owns. B2, below, governs choices the evidence already settles. Neither covers the common case in between: a policy inside **your own** package where no convention applies and no evidence decides, because the question is a **stipulation** — a definition, threshold, taxonomy, severity, or rule-scope chosen, not derived. B2's "asking is the drift" reasoning does not license enforcing a stipulation unilaterally; it licenses not asking when something already decides the answer, which by definition is not true of a stipulation. The test: if the owner asked "why this and not the other?", could you answer with a file, a measurement, or a rule — or only with your own judgement? The second case is a stipulation. Build it, measure the alternatives, present the measurement — but **ship it as a proposal to the owner, not as an enforced artifact** until they rule on it. This is narrower than asking about everything (the owner's own named drift): the ordinary case, where evidence decides, is unaffected by B2b and still governed by B2. Tell: you are about to enforce a rule against real work, and the honest answer to "why this and not the other?" is only your own judgement.

### B2 — Act vs. ask (L-78, Defensive Deferral)
The ceremony's "STOP and ask" covers *inability* (can't complete steps 1–3). It does not cover the opposite failure: **asking when the convention or on-disk evidence already settles the choice.** When a rule or the evidence determines the answer, ACT and report — do not manufacture a decision point. Ask only when a matter is **genuinely undecidable** from the rules and evidence, not when it is merely large, irreversible-feeling, costly, or arriving after a run of prior mistakes. Converting your own low confidence into the user's decision-load is the anti-pattern.

### B3 — Verify-before-ship, distinct from sequence ordering (L-65 / L-66)
The fail-stop covers skipped steps *within a declared sequence*. It does not, by itself, cover **unverified success claims**. Any externally-verifiable claim — "0 violations," "manifest verifies," "merge is consistent," a SHA, a citation, a quoted definition, **or an analytical characterization that grounds a recommendation or disposition** ("class X already fills role Y", "artifact Z is the right home for this record") — must be checked by **re-running the validator / re-parsing the file / reading the source**, not asserted from plausibility. The verification must PRECEDE the claim; writing a decision-driving characterization and then offering "I can verify this if you like" is the tell that the order was reversed (L-65 extension, 2026-06-04). Never relabel an advisory pass (Warning) as conformance (L-66). State the shape/tool version and method in the same sentence as any "0 violations" claim. Tell: you are about to write a pass/clean/consistent claim you have not just re-executed.

This covers negative and impossibility claims identically to positive ones: a stated "cannot be done" or "X does not exist" is exactly as externally-verifiable as "0 violations," and pattern-matching an asked question to a more famous, harder problem is not a substitute for testing the specific claim actually made. Before asserting "no mechanism can X," when a cheap direct test is available, run it. Before "X does not exist anywhere in this framework," check the prose discipline document, the relevant schema/shapes, and the shipped tooling — not one narrow query against one data structure; a single negative result generalizes to nothing beyond what it actually checked.

The verification itself must be genuinely independent of the state it checks, not merely present. A "fresh clone" fetched and inspected in an earlier turn does not verify a claim made in this one; a publish or forensic-compliance claim is not final until the confirming check is run in the same turn as the claim, against the actual current remote/tool output, not assumed from an earlier turn's tool result. Tell: you are about to repeat a verification result from a prior turn instead of re-running it now.

### B4 — Identity before correctness (BP-D2 / BP-D7)
Before acting on a file, confirm *which* file is authoritative and *what* it actually is — not what its name or a summary implies. Two files sharing a name prefix may be distinct artifacts; one ontology IRI carried at two versions is an identity collision, not a duplicate; the named base version may be superseded by a newer one. Read the bytes, group by declared ontology IRI, check the priorVersion chain. Tell: you are trusting a filename, a version number, or a completion report instead of the parsed content.

---

### B5 — Session start: rehydrate before grounding (L-85)
The ceremony presupposes the governed store is present and authoritative — but **the execution container is wiped between sessions** (working tree AND toolchain: rdflib/pyshacl must be reinstalled). You cannot perform ceremony step (2) — extract verbatim `skos:definition` from the ABox — if the ABox is not loaded. So *before* the ceremony can run correctly: do not assume the working tree exists. Rehydrate from the governed store, SHA-verify every file against the internal MANIFEST, re-parse, re-run the validators, and confirm version/state markers. **Then check freshness against origin, which the MANIFEST cannot tell you.** A manifest pass is an INTERNAL-CONSISTENCY result: it proves the snapshot is undamaged, and it is equally true of a snapshot that is one hour or six months stale. Where the store has a remote (a git origin), `git fetch` and confirm zero commits behind before any governed action, and re-check before any write — a parallel session may have pushed while you worked. Where the store is a user-held bundle with no remote, say so explicitly and treat every claim as scoped to that snapshot. Tell: you are about to act on a tree you verified internally but never compared to its origin. If the current bundle is absent, **ASK for it** — do not proceed on a stale on-disk copy or on the memory/context summary (which is narrative, non-verbatim, and not the governed store). There is NO automatic cross-session persistence; the only persistence path is a bundle the user saves and re-uploads. Tell: you are about to ground a claim on files you have not re-verified this session, or on context instead of a re-read artifact.

### B6 — Plural requests answered as if singular (L-113)
When a request names or clearly implies more than one item — categories, findings, tasks — resolving one of them is not license to treat the rest as answered. Give every named item its own explicit disposition: built, confirmed already covered, or declined with a stated reason. A single aggregate judgement that silently drops an item is the tell, even when the item that was addressed was addressed correctly and completely. This is distinct from B2: B2 is about not manufacturing a decision point the evidence already settles; B6 is about not letting a settled decision on one item stand in for a decision on all of them.

### B7 — Label before identifier (L-118)
An identifier is a handle for machines: chosen for uniqueness and brevity, it compresses a sentence into a token and invites the reader to reconstruct the sentence by guessing. A reviewer who cannot read an element cannot challenge it, and a governance framework whose elements cannot be challenged is decorative. Two halves: (1) every governed element you create or discuss carries a one-sentence human label — not a restatement of the identifier, but what the element actually is, in words a reader outside the session can judge. (2) discussion, reports, and changelogs use the label, not the identifier — an identifier appears only where it is needed to act (a path to edit, a term to grep, disambiguating two similarly labelled elements), and then alongside its label, never instead of it. This binds how a session talks to its own owner as much as to peer sessions: answering in identifiers asks the owner to decode rather than to decide, and if the label does not exist, that absence is the finding to report, not a gap to route silently around. Tell: you are about to name, cite, or discuss an ontology element, a lineage stage, or a governed artifact by its identifier alone, with no human-readable sentence attached anywhere in the same breath.

## Run-length rules — shorter runs, the same standards (BP-D55, v2.16.0; R9 v2.17.0)

The governing session's long runs came from the work around the checks, not from the checks. These rules prevent that. Each says whether a gate enforces it or it is advice; a rule found broken twice in the handover log gets a gate in the next release or is withdrawn.

- **R1 One path.** Release with `oe_release` (repo-tooling): package gates, manifest, the publisher's dry-run and, with `--publish`, the publish, then the wait for CI and the tag, in one command (`04-documentation/OE_RELEASE_PATH_v1_1_0.md`). A hand-made sequence (a private manifest script, a partial run of the checks) is not a shortcut. *Gate:* the publisher refuses what a hand-made stage gets wrong (manifest both ways, stowaways, deletions, structure); the tool is how a session gets it right once.
- **R2 Fail early (L-148).** Run the dry-run as soon as the stage exists and after every cluster of changes, not once at the end. *Gate:* none (advice).
- **R3 The same refusal twice means the cause is not known (L-146).** Stop re-running; write the cause in one sentence from what the gate measured, change that, run again. *Gate:* `oe_release` stops the third run (exit 3) until `--cause "<text>"` is given; the cause is kept beside the stage.
- **R4 A step done by hand twice becomes a tool (L-147).** Before the third time it is built, tested with a failing case, and shipped in repo-tooling; a script in a scratch folder is not a tool. The closing handover lists any step still done by hand twice. *Gate:* none (advice).
- **R5 Time limits, and no sleeping.** A command that scans the repository, uses the network or waits carries a time limit; one that exceeds it is a finding to explain, never a command to run again unchanged. Waiting for CI, a tag or any result happens inside the active turn; no scheduled wake-up is used to wait for your own work. *Gate:* `oe_release` limits every step (exit 4) and waits in-process; for other commands, advice.
- **R6 One purpose per release, the checkpoint inside it.** A release changes one thing a reader can name. The plan amendment, the log rows and the state in the next session's handover are written in the release that changes them, not afterwards. A change that leaves another package's gate red until a second release lands (a tool and the copy that must be byte-identical) is declared in the plan before the first publish, with the order. *Gate:* the byte-identity and discipline-consistency checks make a forgotten half visible in CI; the rest, advice.
- **R7 Look before you wait (L-149).** Before recording an item as waiting for a ruling, another session or a decision, search the accepted handovers, the knowledge base and the handover log, and write in the line what was searched. *Gate:* the aggregate generator refuses a new line without `ruling:` in its note; the search itself, advice.
- **R8 Say what you are doing.** Before a step that will take minutes, send one line saying what it is; end every release with the summary line (what was published, CI, tag). *Gate:* `oe_release` prints each step's duration and the summary line.
- **R9 A check that takes minutes runs once per set of bytes (L-150).** Inside one release a package's own gate runs once: the publisher binds a pass to the exact bytes of the stage, the upstream tree the gate reads, the head of the target repository, the Python version and an hour, and the real publish reuses the dry-run's pass. Inside a package's own gate, a validation that reads the same data and rules files in more than one step is run once and its result shared, and one whose inputs are byte-identical to a passing run is not run again (`oe_gate_cache`: only passes are stored; every file the step reads, the checker itself included, is named as a key file). A step that reads what it does not name (the network, the clock) is not cached. No check is removed or weakened: one changed byte, a moved origin or `OE_FRESH_GATES=1` runs everything in full. A gate that really takes minutes is stated up front (R8); the release tool's default limit for publisher steps is 1800 s and `--step-timeout` overrides it. *Gate:* the publisher's receipt (its test shows a receipt that always says valid is caught) and `oe_release` printing "last time ... expect about N s"; sharing and caching inside a package's own gate is advice for that package.

---

## Standing record rules (moved here from the change history, v2.13.0)
Two rules that governed the whole discipline sat only in its change history, where a reader who skips the history never meets them. They are stated here as rules, with their wording unchanged; the change-history entries that first carried them are left exactly as written.

- **The knowledge base governs.** If the ABox lesson text and this file ever diverge, **the ABox is authoritative** (extract it verbatim per step 2).
- **Corrections are appended (L-114).** A historical record is corrected by an appended note, not by rewriting the text that was true of what actually shipped at the time.

## Ontology file structure — one T-Box, one A-Box, one SHACL file per package (BP-D54, v2.16.0)

The unit is the package. A package ships, in all, ONE T-Box file (every class and property), ONE A-Box file (every individual) and ONE SHACL file (every shape), each with ONE `owl:Ontology` header and ONE version. No file mixes roles. No extension, follow-up, addition or patch file sits beside them: a change goes into the canonical file as a new version of the whole file, and the old version leaves the package. File names follow BP-D6. What used to be a separate subject becomes a **module** inside the three files: terms keep their IRIs, and the module is an untyped resource at the former subject's IRI with `dcterms:isPartOf` (the package ontology IRI), `dcterms:identifier`, `rdfs:label` and its own `owl:versionInfo`. A package's retired history is held the same way in its folder `archive`: one T-Box, one A-Box, one SHACL file; every complete retired state stays recoverable from git history and release tags. The full rule, the owner's words and the later rulings are in the knowledge base (BP-D54 and its change notes); the knowledge base governs.

**Where the unit ends.**
- Files outside the domain (lineage, governance, maintenance) are units of their own that also meet the rule; a role with zero files is allowed. Examples may be a unit of their own. A unit is marked by a `VERSION.txt` in its folder and named by a row of the class table.
- Registrations obey the same rule: the registrations are one unit and each registrant is a module. A later registration is added with `oe_register_unit` in extend mode, never as a new file.
- Generated shape files leave the package; copies of another package (`vendored…`, `…-snapshot`) and deliberate test inputs (`fixtures`) are read by the tools only as their class says.
- **One class table** (`OE_STRUCTURE_CLASSES_v*.tsv`, read through `oe_structure_classes_v*.py`) decides what each tool reads or skips; no tool keeps a list of its own (L-144).

**The rules and their gate.** One checker, `oe_structure_check`, reads parsed content, runs on every push to every package (CI Gate N) and in the publisher, and fails on any violation not in the debt register:

| Rule | Forbids | Switch |
|---|---|---|
| N1 | a file name that does not match `<name>_v<MAJOR>_<MINOR>_<PATCH>.ttl` | always |
| N2 | a name that says extension, follow-up, addition, patch, re-emit or draft | always |
| V1 | two versions of one file side by side | always |
| R1 | a file that mixes roles (T, A or S) | always |
| H1 | more than one `owl:Ontology` header in a file | always |
| U1, A1 | more than one active file of a role in a package (U1), or in its archive (A1); a count that grows fails | always |
| M1 | a named subject without `dcterms:isPartOf` its module | on by an `enforce` line in the package's register |
| D1 | identical anonymous copies under one subject and predicate (L-143) | on by an `enforce` line |
| X1 | a nested folder with its own `VERSION.txt` that no class-table row names | always |

**Debt.** Each package carries its own register of dated debt; governance keeps the rules and a generated aggregate that is the ceiling. A package's register may only shrink what the aggregate records or add nothing it lacks; the aggregate rises only with a `ruling:` in the line's note, and `oe_debt_aggregate --verify` runs in CI. Each owning session clears its own entries.

---

## Cross-session enhancement handovers — the handover inbox (L-115)

Any genuine enhancement finding for OE — from another package's session, or from OE's own work
surfacing something about itself — is built as a handover document, not folded silently into a
response or buried in a package-private location. This is adapted directly from
`a registrant package`'s own real, working design (`07-handover-inbox/`), not invented
fresh: that package's inbox has processed real cross-session proposals to a working disposition
(`accepted`/`rejected`/`deferred`) for a long enough history to prove the mechanism, including
one of OE's own prior findings being received, reviewed, and substantively acted on there.

**The directory, governed by OE:** `oe-pack/07-handover-inbox/`, with `pending/`, `accepted/`,
`rejected/`, `deferred/` subdirectories and a plain-text `HANDOVER_LOG.md` — RDF is deliberately
not used for this; it is bookkeeping ("has this been looked at, with what outcome"), not domain
knowledge. `pending/` holds anything not yet reviewed; any OE-compliant session (`oe-pack`,
`oe-method`, `repo-tooling`, and any future package adopting this discipline) checks it at
session start, as a standing ceremony step. On review, the file moves to `accepted/`,
`rejected/`, or `deferred/`, and a line is added to the log. Nothing pushes here automatically —
no session starts itself; an item arrives because the owner places it, or because a session
archives a received handover here for future sessions to find without re-uploading it.

**Direction matters.** A proposal arriving *at* OE goes in OE's own inbox. A proposal OE sends
*to* another package goes into **that package's own inbox**, where one exists — matching how
`a registrant package`'s inbox received and logged OE's own outgoing finding. Filing an
outgoing proposal only in OE's own documentation, for the target session to discover by chance,
is the weaker path and should be the fallback, not the default, when the target has a real inbox
to receive it properly.

**Every accepted or rejected item's log line states the verification actually performed** — per
B3, the disposition is itself an externally-verifiable claim ("this was independently checked
against real artifacts before being adopted"), not a summary of how persuasive the proposal read.

## Registration maintenance — a real ceremony, mirroring the handover inbox (L-120)

A closed `ORCP` registration is a snapshot, not an ongoing guarantee. `Phase G` assumes the
registrant will proactively re-emit when something changes; nothing structural asks the inverse
question periodically — has enough changed since closure that revisiting it is worth asking
about. Confirmed concretely: two closed registrations (`variant-algebra`/an algebraic framework, `an integration blueprint`/an integration blueprint) had
both drifted badly from their registered baseline with nothing surfacing it until asked directly.

**The directory, governed by OE:** `oe-pack/08-registration-maintenance/`, with
`REGISTERED_SUBJECTS_v*.tsv` (the registry: subject, live repo location where known, registered
version, closure pack version) and `REGISTRATION_MAINTENANCE_LOG.md` — the same shape as the
handover inbox (`L-115`), deliberately: a real place with a log, not a threshold buried inside
`Phase C`'s gate logic. Every run is logged, including a run that finds nothing to flag, so
absence of action is itself visible rather than indistinguishable from a check that never ran.

**The check, run by `03-tooling/registration_maintenance_check_v*.py`:** fetch each registered
subject's live current version where a repo location is known; flag when either a **MAJOR** bump
or **5+ accumulated MINOR** bumps have occurred since registration. A subject with no known,
verifiable live location, or a registration with no version baseline, is disclosed as
`UNCHECKED`/`UNVERIFIABLE-BASELINE` — never silently skipped, never guessed at to fill the gap
(`BP-D28`/`L-57`).

**The tool reports; it does not act.** Flagging is not a ruling and does not force a reopen —
filing the resulting handover, if any, stays a deliberate session action using the existing
handover-inbox mechanism, and reopening the registration is the registrant's own decision (`B1`).



- **Scope discipline (L-64):** every individual, narrative, `dcterms:source`, `skos:definition`, comment, and query body you author must stay inside the relevant package's vocabulary. No scope-foreign terms bleeding across sessions.
- **Version semantics (BP-D7):** every release is a correct SemVer bump with `owl:versionInfo` == `owl:versionIRI` == filename token, and a recorded `owl:priorVersion`. PATCH (`x.y.z→x.y.z.1`) for fixes with no vocabulary change — always preferred for fix-only. MINOR for backwards-compatible additions. MAJOR for removals/renames. **A changed file always gets a new version; never reuse a version for changed content.**
- **No multi-version clutter:** the package ships one current file per ontology identity. Superseded versions are retired (with a release-history record), not carried alongside. Legitimate `tbox`/`abox`/`shacl` triads sharing a subject IRI are distinct artifacts, not duplicates — do not conflate.
- **Provenance:** record each release in the release-history ABox; regenerate and self-verify the MANIFEST after any content change.
- **Upload hygiene:** inventory uploads + sizes first; read slices, never full-cat >200 KB; ship large text in a `.zip`.
- **Session close — record emergent lessons (L-84):** before a release is considered complete, ask "did clear, genuinely-new lessons emerge this session that are not yet in the ABox?" If yes, record them into the governed store now (not only cite them in prose). **Scope guard:** this covers only lessons that genuinely emerged and pass the duplicate-screen against existing BP/Ls — it is NOT a quota; recording an empty or duplicate lesson to satisfy a checklist is the opposite failure (L-71).
- **Classify findings at logging time (L-114):** when disclosing a finding — a defect, a gap, a discrepancy — state explicitly whether the outcome would have occurred if the relevant safeguard had never existed. If no, it is evidence the safeguard works, not a gap in it, and must carry that label rather than being filed with the same weight as a genuine gap. Logging every friction point as if it were a finding, regardless of whether it reflects a real deficiency or a safeguard doing its job, reads as diligence but dilutes real signal.
- **Consolidate before creating (L-119, `BP-D52`):** before adding a new file, directory, fixture, deposit, or similar per-instance artifact to address a specific need, name the closest existing one and check whether it can be extended, rather than defaulting to a new artifact every time. This is a general pattern, not a fixture-specific one — the same additive-only-growth shape recurs under different names (fixtures; earlier, patch files) whenever the check is skipped. A gate needing its own proof it can fail (`B3`/`L-95`) needs its own *proof*, not its own directory — a shared tree can carry proofs for several gates at once. Not a rule against ever creating something new: a genuinely distinct concern still gets its own artifact. But check consolidation first; verify the consolidated version genuinely still proves what it replaces before removing the original. **Distinctness test:** a need is genuinely distinct when the closest existing file's own name, under `BP-D6`, would have to misdescribe its content or describe two things at once if the new content were folded in — this cuts both ways, against rationalizing a new file *and* against cramming unrelated content under a name that no longer fits.
- **Response economy:** simple narrative by default; details only when asked; no option menus on settled questions (B2/L-78); no filler hedges on settled rules.

---

## Governance provenance in repositories others can read (owner ruling, 2026-09-24)

Governance is private: `oe-pack` is the working source and `oe-method` the reference location, both in
a private repository; the `oe-method` mirror is private and shared by invitation. Packages governed by
this discipline may be published into repositories that others can read — course repositories are
readable by students.

**The ruling:** in such a repository, governance provenance is a **citation for the governance
owner**, not something its readers are expected to verify. **No governing text — discipline, knowledge
base, shapes — is copied into it** to make the citation checkable; copies drift, which is the failure
forked discipline warns against.

**Said explicitly, never implied:** the publisher measures the governance repository's visibility at
publish time and writes it into every publish record, together with a plain statement of what a reader
can and cannot verify. A record that cites private governance without saying so is a defect.

## The release path (BP-D55, v2.16.0; limits and receipts v2.17.0)

```
python3 repo-tooling/oe_release_v*.py <stage> <slug>              # gates, manifest, dry-run
python3 repo-tooling/oe_release_v*.py <stage> <slug> --publish    # the same, then publish, CI and tag
python3 repo-tooling/oe_derive_method_v*.py <method-stage> --pack <pack> --tooling <repo-tooling>   # the derived package
```
The page `04-documentation/OE_RELEASE_PATH_v1_1_0.md` says what each step does, what each refusal means and how to clear it, and the three orders that are not obvious (a tool and its byte-identical copy; a change of the class table; the derived package). Nothing on this path removes or loosens a check. Its steps have their own limits (checks 280 s, publisher steps 1800 s) and it prints the last measured duration before it starts (R8, R9).

---

## v2.17.1 (2026-10-07, generalised variant)
Same relationship as the earlier variant notes in the change history: this file and the development source's `OE_Operating_Discipline_v2_17_0.md` carry the same governing rules, generalised for this package's distributable copy. Carries its own token, per the release-gate discipline-consistency check.

## v2.17.0 (2026-10-07)
On the owner's question of 2026-10-07 whether more could be done for packages whose own gate takes many minutes ("If so, let's do it"), after a parallel session reported that the discipline v2.16.1 would not shorten a gate that re-validates its whole data and rules files cold: adds rule R9 (a check that takes minutes runs once per set of bytes) with its gate stated, the publisher's gate receipt (repo-tooling 1.45.0), the gate cache tool for a package's own validation steps, per-step limits suited to long gates and a "last time" line in `oe_release`. KB: L-150; BP-D55 text updated. No check was removed or loosened; no rule of the ceremony or of B1 to B7 changed.

## v2.16.0 (2026-10-07)
On the owner's direction of 2026-10-07 ("update the OEE discipline under the new rulings and enforce the application of the OEE rules in a concise way ... include preventive rulings and enforcements against long runs"): the structure section is rewritten to the rules and rulings in force (BP-D54 and its change notes; rules M1, D1 and X1, the class table, own registers and the aggregate, units outside the domain, the registration unit); the eight run-length rules R1 to R8 and the release path are added (BP-D55, L-146 to L-149); the change history moved, unchanged, to `OE_Operating_Discipline_CHANGELOG_v1_0_0.md`. No rule of the ceremony or of B1 to B7 changed.
Earlier history: `OE_Operating_Discipline_CHANGELOG_v1_0_0.md`.
