# OE Operating Discipline — change history (v1.0.0 CHANGELOG, 2026-10-07)

Moved here, unchanged, from `OE_Operating_Discipline_v2_15_0.md` and the earlier versions of that file, which carried it below the rules (about half of the file). The text of every entry is exactly what was true when it was written; a correction is appended, never made in place (L-114). The current rules are in `OE_Operating_Discipline_v*.md`; the entry for v2.16.0 and later is kept there and moved here when the next version is made.

## v2.15.1 (2026-10-06, generalised variant)
Same relationship as the earlier variant notes below: this file and the development source's `OE_Operating_Discipline_v2_15_0.md` carry the same governing rules, generalised for this package's distributable copy. Carries its own token, per the release-gate discipline-consistency check.

## v2.15.0 (2026-10-06)
Changes the unit of the ontology file structure from the subject to the package (BP-D54), on the owner's ruling of 2026-10-06 ("No, not per subject. All subjects should be consolidated in one file per concept and at the end we will have just 1 file for A-Box, 1 file for T-Box, and 1 file for SHACL"), settled in the governance session: one T-Box, one A-Box and one SHACL file per package; former subjects become modules inside; the archive is one triad per package. BP-D53 stays as the record of the earlier rule with a changeNote; its parts on role purity, names, versions and the register stand. Enforcement: `oe_structure_check` v1.1.0 (rules H1, U1, A1 added, I1 retired).

## v2.14.0 (2026-10-05)
Adds the section "Ontology file structure" (BP-D53). The owner's question of 2026-10-05, why the new ontologies are loose single files and the traditional ones drift from the naming and version conventions, was checked against the files: the three-file rule existed only as a comment on a quality criterion (citing it under an identifier that resolves to a different rule) and as comments in four shipped A-Boxes; the checks it named were in an external bundle that is in no repository; and the automated gates ran only for one package's folder. Measured at the time: 27 of 166 parsed files mix roles, 21 names break the naming pattern, 10 identities ship several versions side by side. Nothing earlier is rewritten (the standing record rules).

## v2.13.0 (2026-10-05)
Moves two rules that lived only in this change history into the rule sections (new section "Standing record rules"): the knowledge base is authoritative when a lesson's text and this file diverge (until now only in "What did NOT change from v1.0.0"), and a historical record is corrected by an appended note, not by rewriting (L-114, until now only in the v2.6.0 note). No rule is added or changed; the wording is the original wording. The purpose is measurable: with every rule in the rule sections, a session can read the rules in full and the change history as headings (`oe_ceremony_digest_v1_0_0.py`) without losing a rule, about 35 % fewer tokens per ceremony (a parallel session's measurement, 2026-10-05; the owner ruled the same day). The history entries are unchanged, per the second rule itself.

## v2.12.0 (2026-09-24)
Adds **governance provenance in repositories others can read** — the owner's ruling on a question
the CME session raised deliberately before its first course repository existed: private governance
is cited, not copied, and every publish record says so explicitly (publisher v1.8.1 measures and
records the governance repository's visibility). Also current as of this version: links to the
discipline and knowledge base point to `oe-method` (repo-tooling v1.15.0+); the publisher can publish
into standalone repositories, including a package at the repository root (v1.8.0).

## v2.11.0 (2026-09-10)
Adds **registration maintenance** as a real ceremony (`L-120`), mirroring the handover inbox's
own shape rather than a threshold buried in a gate — the owner's own operational proposal.
Prompted by a direct impact-analysis request that found an algebraic framework's and an integration blueprint's closed registrations both
badly stale: an algebraic framework moved from registered `v1.4.0` to a live-fetched `v2.20.0` (a MAJOR bump) during
the session's own investigation, with real architectural changes occurring twice mid-investigation;
an integration blueprint's dependency shape on an algebraic framework changed twice since its own registration closed, with zero
remaining references to the pinned dependency anywhere in current tooling.

New directory `oe-pack/08-registration-maintenance/` (registry + log) and
`03-tooling/registration_maintenance_check_v1_0_0.py`, tested both directions before the first
real run was logged: a synthetic within-threshold case correctly reported `OK`; the real an algebraic framework case
correctly reported `FLAG`, independently reproducing a finding already acted on via a direct
handover earlier the same session. The tool only reports — filing any resulting handover stays a
deliberate session action through the existing inbox mechanism; reopening a registration remains
the registrant's own decision.

## v2.10.1 (2026-09-10)
Adds a **distinctness test** to `BP-D52`, on direct follow-up: should the rule push harder
toward reusing existing files? Checked first rather than strengthened by default — no
counter-lesson against over-consolidation existed, but `BP-D6` (file naming must represent the
file's own content) already bounds how far reuse can go, and pushing further would put `BP-D52`
in tension with `BP-D6` and `BP-D7`'s one-lineage-per-artifact principle. The test: a need is
genuinely distinct when the closest existing file's own name would have to misdescribe or double
up if the content were folded in — cuts both ways, against a needless new file and against
cramming unrelated content under a name that no longer fits. A real parse error (a multi-
paragraph value written with the wrong string-quote syntax) was caught by re-parsing before
claiming success, not assumed correct from the edit alone.

## v2.10.0 (2026-09-10)
Generalises the **consolidate before creating** standing rule (`L-119`), on direct challenge:
the owner pointed out the same additive-only-growth pattern had occurred before with patch
files, not only with fixtures, and asked whether the lesson as written would actually generalise
to a future recurrence under a different name. It would not have — the label and prose were
scoped specifically to "fixture or deposit." Extended `L-119` additively (matching `L-47`'s own
precedent: original text preserved in full, extension recorded separately, not a rewrite), and
added **`BP-D52`** as the operational form: before creating a new file or directory for a
specific need, name the closest existing artifact and check it for extension first. The prior
patch-files incident could not be independently re-located in the current tree at extension time
— disclosed rather than silently assumed resolved or silently taken on faith.

## v2.9.0 (2026-09-10)
Adds the **consolidate-before-creating** standing rule (`L-119`), from the owner's own direct
observation: 27 fixture files had accumulated across `oe-pack` and `oe-method` with no
consolidation step ever considered — one new directory per new gate, additive-only, forever.
Placed alongside `L-84`/`L-114` as a specific-moment practice, not a new numbered boundary,
since it governs one recurring decision (whether to create or extend) rather than a whole class
of action. Applied in the same session it was written, not left theoretical: `oe-method`'s three
separate per-gate negative fixtures (10 files) were consolidated into one combined fixture
(6 files) that fails all three custom gates from a single small tree — each gate re-run directly
against the consolidated version and confirmed to genuinely still fail for its intended reason
before the originals were removed, published, and independently re-verified on a fresh clone.

## v2.8.0 (2026-09-10)
Adds **B7** (label before identifier, `L-118`), from a real, independently-verified cross-session
handover (`a registrant package`, 2026-09-10): the owner stopped a working session with "I
really don't understand as you use a mixed language, not human readable and I cannot follow the
inferences you made from the ontologic item names." Checked directly before adopting: the
specific SHACL shape the handover cited (`IntentElementLabelShape`) was not found under that
name in that package's current shapes file, but the underlying data claim held exactly — a
direct query against the register found precisely 12 of 24 checked intent elements carried
neither `rdfs:label` nor `hasTitle`, matching the handover's own count. Two halves: every
governed element carries a one-sentence human label, and discussion — reports, changelogs,
answers to the owner — uses the label, not the identifier, except where an identifier is needed
to act.

**A real, live data corruption was found and fixed while registering this boundary's lesson,**
disclosed here rather than silently repaired: the v2.4.0-era edit that added `L-116`/`L-117` to
`knowledge_base_abox` had silently dropped `L-26`'s own subject declaration, leaving its
properties attached to `owl:NamedIndividual` — the OWL vocabulary term itself — rather than to a
proper individual. This was live and unnoticed for a full release cycle; the verification at the
time checked total triple count and overall parse validity, never that content near an insertion
point stayed correctly attached, which is the actual gap `knowledge_base_abox` v2.25.0 closes.
Restored from the last known-good published state and re-verified comprehensively: every lesson
and best-practice subject checked individually, not by parse count alone.

## v2.7.0 (2026-09-10)
Adds **B2b** (derivable versus stipulated decisions inside a session's own package, `L-116`),
from a real, independently-verified cross-session handover (`a registrant package`,
2026-09-10). B1 governs artifacts another session owns; B2 governs choices the evidence already
settles; neither covered the common case of a policy inside a session's own package that the
evidence does not decide — a stipulation. Checked directly before adopting, not accepted on the
strength of the argument: confirmed `G85`-`G92` exist in that package's own lineage discipline,
and that a spot-checked entry (`G89`) genuinely opens by citing an owner correction of exactly
this pattern (a rule enforced unasked, then corrected). The finding measured 11 of 18 recent
SHACL shapes as the filing session's own stipulations and 7 of the last 8 `G`-entries as owner
corrections of one — both counts independently confirmed present, not re-derived from scratch.

Also registers `L-117` (a rule whose reach is decided by its author, not its adopters, is a
retroactive-enforcement failure) as a supporting knowledge-base entry the same handover named —
distinct from `L-116` because this pattern can recur even when a stipulation is properly
proposed and approved, if its enforcement is then applied backwards over work predating it.

## v2.6.0 (2026-09-09)
Repoints B6, the finding-classification rule, and the handover-inbox section header from
`L-111`/`L-112`/`L-113` to `L-113`/`L-114`/`L-115`. A real cross-session finding
(`vaf-agentic-pipeline`, 2026-09-09) verified directly, not accepted on its own report: the
v2.4.0/v2.5.0 notes below cited these three rules under IDs that either already belonged to
unrelated lessons (`L-111` was documentation-coverage drift; `L-112` was mechanical-repoint
file-class discipline, both registered before v2.4.0 existed) or were never registered at all
(`L-113`). This is L-84's own case, applied and cited across many turns with the underlying
lessons never written to the governed store — and the same collision shape a much earlier
release (`knowledge_base` ABox v1.32.0) already hit and fixed by renumbering, checked as
precedent before choosing the same remedy here. The three lessons are now registered in
`knowledge_base_abox` v2.23.0 under the free IDs. The v2.4.0 and v2.5.0 notes below are left
exactly as written — per this release's own new L-114, a historical record is corrected by an
appended note, not by rewriting the text that was true of what actually shipped at the time.

## v2.5.0 (2026-09-06)
Adds the cross-session handover inbox (`L-113`) as a standing OE-wide practice, requested
directly: adapt `a registrant package`'s own proven enhancement-handover protocol so it
becomes common practice for any OE-compliant ontology, not something improvised per finding.
Reviewed that package's real, working design (`07-handover-inbox/`, its `HANDOVER_LOG.md`, and
its own disposition history — including OE's own prior finding being received, reviewed, and
substantively acted on there) before adapting it, rather than inventing a shape from description
alone. `oe-pack/07-handover-inbox/` built with the same four-way disposition
(`pending`/`accepted`/`rejected`/`deferred`) and the same plain-text, non-RDF log rationale.
Migrated the one item this discipline had already substantively processed
(the agentic-drift-lessons handover behind v2.4.0) into `accepted/` with a log line, rather than
leaving it in a package-private documentation folder now that a proper inbox exists.

## v2.4.0 (2026-09-06)
Adds **B6** (plural requests answered as if singular, L-111) and a **finding-classification standing
rule** (L-112); enriches **B3** with three clauses on negative and impossibility claims, verification
independence, and multi-source checks before non-existence claims. Source: a genuine cross-session
handover (`HANDOVER_a registrant package_to_OE_agentic-drift-lessons_v1_0_0.md`), filed by the
`a registrant package` session after an owner-requested review of one extended conversation
building and closing a lineage autonomously. Five drifts were reported; each was independently
verified against real, checkable artifacts in that session's own discipline history (G1, G6,
`backlog_roadmap_report_v1_6_0.py`, G72, G77, G78 all confirmed present and matching in specific
detail) before any of this was written — accepted on the evidence, not on how well the handover read.

First filed as a standalone checklist in `oe-pack`'s own documentation, which was the wrong home:
the concepts are generic to any OE-compliant session, not particular to this package, and a
package-private file is invisible to every other session this discipline is supposed to govern.
Corrected here, in the shared document both `oe-pack` and `oe-method` carry identically.

Three of the five drifts (test-before-impossibility-claims, independent verification, multi-source
non-existence checks) enrich B3 rather than mint three new siblings, following the same precedent as
B5's own v2.3.0 enrichment: B3 already governs "a claim requires prior verification, not plausibility,"
and each of the three is a specific, real instance of that same gap, not a distinct boundary. One
(per-item disposition on multi-item requests) is genuinely distinct from anything B1-B5 cover and
becomes B6. One (finding classification) is a practice for a specific recurring moment — logging a
finding — matching the placement and voice already used for L-84, not a boundary about a whole class
of action.

Independent corroboration, not just accepted on report: the filing session's own Drift 4 — verifying
structure while asserting operational compliance, a narrow accurate check mistaken for a sufficient
one — is not abstract to OEE governance either. This session reported a series of `oe-method`
publishes as successful and independently verified when they were not; GitHub's own event log,
checked only once asked to investigate directly, showed no push to that repository after a much
earlier version. The enriched B3 clause on verification independence is written from that experience
directly, not only from the handover.

## v2.2.0 (2026-07-02)
Pointers made **version-independent** (resolution-rule section added): the governance source and all artifact
references now resolve by pattern to the highest SemVer instance in the attached pack, and the in-pack copy of
this discipline is declared authoritative over any detached copy. Trigger: a parallel session read a stale
detached copy (pointer `v2_5_0`) against a pack carrying `v2_10_0`. Honest regularization: prior global repoints
had mutated v2.1.2's pointer text in place (v2_7_0 -> v2_10_0) **without a version bump** — a same-version content
change (the BP-D7 slip class RADAR once flagged), evidenced by SHA drift of the v2.1.2 file (1d5d78f3 -> f3fa1ab1).
This bump regularizes that and removes the mutation surface entirely. Companion tooling fix: `release_check` is
now self-contained (v1.7.0 replaces the v1_6_x chain that hard-required an unshipped v1_5_2), and
`regression_suite.py` exits NOT-APPLICABLE (0) cleanly when the F-phase ecosystem dir is not shipped.

## v2.1.2 (2026-06-07)
PATCH: governance-source pointer updated to `knowledge_base_abox_v2_10_0.ttl` (was v2_2_0, was v1_35_0). No behavioral boundary/rule change. Bumped per BP-D7 after RADAR correctly flagged a same-version content change.

## v2.1.0 additions (2026-06-04)
v2.1.0 adds **B5 (session-start rehydration, L-85)** and a **session-close standing rule (record emergent lessons, L-84)** — the two temporal points the per-action ceremony structurally does not reach (start and close, vs. pre-action). It also sharpens **B3** to cover decision-driving analytical characterizations (L-65 extension), and corrects the stale governance-source path to `knowledge_base_abox_v2_10_0.ttl`. L-86 (prefix/quote-before-Turtle-append) was deliberately NOT elevated here: it is within-artifact correctness already caught by the ceremony's re-parse enforcement, so it stays an ABox lesson, not a prompt-level boundary.

## What did NOT change from v1.0.0
The three-step ceremony and the fail-stop-on-skipped-X rule are unchanged — they work and have repeatedly caught real defects. v2.0.0 only adds the four boundaries (B1–B4) and the standing operating rules, which restate lessons already in the OE ABox so they are visible at prompt level, not only retrieved mid-action. If the ABox lesson text and this file ever diverge, **the ABox is authoritative** (extract it verbatim per step 2).

v2.3.0 enriches **B5** with a freshness-against-origin step. Raised by a parallel session, upheld on bytes: B5 as written prescribed only `SHA-verify every file against the internal MANIFEST`, which is an internal-consistency check and silent about whether the snapshot is current. That session executed B5 faithfully every turn and the gap remained, so the defect was in the boundary's design, not its execution. The gap is not an authoring error — B5 was written when the only persistence path was a user-held bundle, where the bundle IS the origin by definition and there is nothing to be behind. A git remote was added later, creating an origin that moves independently, and the discipline had not caught up with its own infrastructure. Evidence that it bites: a push in the same session was rejected non-fast-forward because a parallel session had pushed first — the gap surfacing after the work rather than at ceremony time. Enriched per L-110 rather than minting a new boundary: B5 already governs session-start rehydration, and what it lacked was one clause, not a sibling rule.

