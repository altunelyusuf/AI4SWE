# OE Pack v19.7.3 — Producer-Side Remediation Report (R1–R4)

Built 2026-05-27. Framing B (make v19.7.3 a clean, self-consistent release). All changes on a working
copy; originals preserved. Every claim below verified against the actual files.

## R1 — INSTALL.md header (DONE)
"OE Pack v17.2.0 — Installation…" → "OE Pack v19.7.3 — Installation…". Pure doc fix.

## R2 — Release-history ABox updated (DONE)
oepack_release_history_abox: added 11 orh:File_* release records for v19.7.3 (the measurement fix +
the 9 renamed files + meta_abox), each with real SHA-256, versionInfo, and PROV attribution, mirroring
the existing orh:File_* pattern. Release-history now references v19.7.3 (was: only 19.7.0). Parses OK.

## R3 — versionInfo↔versionIRI alignment (DONE) — 18→0 mismatches
Two-tier evidence rule applied per file (BP-D7 + OntologyFileConvention/C8-V):
- **Tier 1 (9 files): versionIRI authoritative** — versionInfo+filename were stale because versionInfo
  was ≤ the file's own maxPriorVersion (logically impossible). Renamed UP to true version:
  - ae_abox 1.0.0→1.4.1, ae_tbox 1.0.0→1.3.3, configuration_abox 1.0.0→2.4.2,
    configuration_tbox 1.1.1→2.3.4, knowledge_base_abox 1.8.0→1.34.0, knowledge_base_tbox 1.2.0→1.34.0,
    measurement_abox 1.3.0→2.7.2, testing_abox 1.0.0→1.2.1, testing_tbox 1.1.0→1.2.1.
- **Tier 2 (9 files): versionInfo authoritative** — filename==versionInfo (C8-V), versionIRI was the
  stale/lower side. Corrected versionIRI up to versionInfo; NO rename:
  - core_tbox, meta_tbox, both oepack_release_history, performance_tbox, quality_abox, quality_tbox,
    reliability_tbox, risk_tbox.
- **meta_abox**: filename stale (versionInfo==versionIRI==1.1.3, filename said 1.2.0) → renamed to v1_1_3.
- Verified: 0 remaining versionInfo↔versionIRI mismatches; 0 C8-V violations on standard subject files;
  49/49 TTL parse.

### Renaming safety (verified, not assumed)
Renaming the 9 Tier-1 files breaks nothing: owl:imports target ontology IRIs (e.g.
<http://example.org/measurement>), NOT filenames; tooling takes files as args (no hardcoded names);
the MANIFEST is regenerated each build. Confirmed by grep across the pack before renaming.

## R4 — Gate verdict (UNCHANGED LIMIT, honestly carried)
Still no single authoritative SHACL verdict asserted. The bundled a reliability ontology suite/tooling are v18-era
(redo_shacl_v4_1_0); a clean v19 verdict needs the c7plus validator + HermiT or a v19-matched a reliability ontology
suite. What IS verified: structural completeness, 49/49 parse, SHA-anchored manifest, and now zero
version-metadata mismatches.

## FLAGGED (not auto-fixed — non-standard, needs a decision)
- **redo_v2_5_18.ttl**: declares ontology `reliability` at versionInfo 2.5.12 (not 2.5.18 as the
  filename suggests) and carries a stray `reliability#testedBy a owl:Ontology` triple (a mistyped
  declaration also present in reliability_tbox). Irregular redo-fragment naming scheme — left as-is
  rather than guess a rename. Recommend: separate review of the redo extension-fragment naming.

## PROPOSED CONVENTION ADDITION (for review)
**Lesson L-DD "Defensive Deferral":** When the catalogue/convention or on-disk evidence already
settles a choice, ACT and report — do not manufacture a decision point for the user. Asking is only
warranted when a matter is genuinely undecidable, not merely large, irreversible-feeling, or arriving
after a run of errors. Anti-pattern: converting the author's own low confidence into the user's
decision-load, because a question cannot be "wrong" the way an action can. This offloads the author's
risk onto the user's confirmations. Complement to L-50 (do not over-ask) and L-52 (do not silently
under-disclose): L-DD says do not ask about what is already settled.

## v19.8.0 — Package version bump (user-identified, convention-confirmed)
The user noted the package kept the same version (v19.7.3) despite file changes. Checked against BP-D7:
correct — when files change, the package version MUST increase. Classification of this pass:
- knowledge_base_abox gained the L-78 individual = backwards-compatible additive = MINOR.
- No class URIs removed/renamed (verified: renamed FILES are not renamed CLASSES; class sets identical
  before/after), so not MAJOR.
=> Package v19.7.3 -> v19.8.0 (MINOR). knowledge_base_abox 1.34.0 -> 1.35.0, metadata aligned, 1.34.0
   recorded as priorVersion.

## L-78 Defensive Deferral — now formalized in the ABox
kb:Lesson_L_78_DefensiveDeferral added to knowledge_base_abox (skos:definition, dcterms:source,
PROV attribution) mirroring the existing kb:Lesson individual pattern. Parses + queryable.

## v19.9.0 — Authoritative gate verdict + v19-matched a reliability ontology suite

### P1 — C7+ TypeDeclarationShape gate (first authoritative verdict ever recorded)
Ran via the real `c7_plus_validator_v1_0_0.py` over the merged data graph (35,155 triples).
**Verdict: NON-CONFORMS, 8 violations.**

All 8 are the same pattern: individuals declared with a type whose class is not declared as
`owl:Class` anywhere in the merged graph. Genuine, confirmed via independent rdflib lookup:

| Type-class undeclared as owl:Class | Affected individuals |
|---|---|
| `reliability#Metric` | Metric_CQCoverage_v17_30_0, Metric_DTUseRate_v17_32_0_pre, Metric_ShaclCoverage_v17_32_0 |
| `reliability#Mitigation` | Mit_RetargetHermitBenchmark, Mit_Step2SemanticShapes |
| `reliability#Process` | Process_v17_32_0_Release, Process_v17_33_0_Release |
| `risk#Mitigation` | Mit_RetargetHermitBenchmark |

These are real defects in the reliability/risk TBoxes (missing `owl:Class` declarations). Flagged
for fix in a follow-up; not auto-patched in this release.

### P2 — HermiT OWL consistency: COULD NOT RUN (environment friction, recorded honestly)
HermiT.jar + Java 21 are on disk, but two distinct bridge bugs blocked execution:
1. owlready2's `_save()` is broken in this Python (`unexpected keyword argument 'commit'`).
2. Direct `java -jar HermiT.jar --consistency` tries to fetch `owl:imports` as a URL and times out
   (no catalog.xml resolution at CLI level).

The reasoner is present and the data is well-formed (parses fully via rdflib + loads into owlready2,
which surfaced **one additional finding before crashing**: `reliability#ReliabilityConcept` has a
**cyclic subClassOf**). Recording this as a known limit + a real defect surfaced incidentally.

**Honest verdict status:** structural SHACL gate (C7+) ran and produced an authoritative count;
OWL consistency check did not run. The "no single authoritative SHACL verdict" objection is
PARTIALLY CLEARED — C7+ verdict is now on record; full HermiT consistency remains open.

### P4 — v19-matched a reliability ontology suite authored (`redo_shacl_v4_1_0.ttl`)
Empirical finding that reshapes the work scope: the v18 suite (`redo_shacl_v4_1_0`) targets
classes RETAINED in v19 (`reliability`, `owl:Class`, `amod`) — not the renamed `ontology-engineering`
namespace. Validated by running v18 suite over v19 data: 1302 results matched (10 Violation, 746
Warning, 546 Info) — shapes are firing, not going dead. So the "v18-era" gap was provenance-deep,
not coverage-broken.

**P4(a) DONE — re-issued as `redo_shacl_v4_1_0.ttl`:**
- versionInfo and versionIRI aligned at 3.0.0 (was 2.0.13.2 / 2.0.13.1 — C8-V violations in the
  v18 file itself, now fixed).
- Both v18 and v19-matched cuts bundled (`redo_shacl_v4_1_0.ttl` retained for provenance).
- Targets `reliability`, `owl:Class`, `amod` — confirmed live against v19 data.

**P4(b) DOCUMENTED FOLLOW-UP — coverage extension:** the v3.0.0 suite carries the same 48 NodeShapes
as v18; it does NOT yet add C1-C8 coverage for the v19-renamed/new subjects (`knowledge_base`, `ae`,
`measurement`, `testing`, `configuration`). That extension would be ~5×5 = 25 new NodeShapes,
authored from scratch. Scoped here as P4(b); not built in this release.

### Objection status after v19.9.0
- **Objection #1 (v18-era a reliability ontology suite)** — PARTIALLY CLEARED. Provenance gap fixed by v3.0.0
  re-issue with v19-matched attribution. Coverage extension (P4b) remains as documented follow-up.
- **Objection #2 (no authoritative verdict)** — PARTIALLY CLEARED. C7+ verdict on record (8
  Violations, diagnosed). HermiT could not run due to bridge tooling bugs — recorded as a real
  limit, not papered over.

### v19.8.0 → v19.9.0 (MINOR per BP-D7)
- Added: `redo_shacl_v4_1_0.ttl` (new vocabulary file, backwards-compatible).
- Added: P1 verdict + diagnosis in this report.
- No class URIs removed/renamed; no breaking changes.

## v19.10.0 — C7+ violations cleared + cycle fix + P4(b) coverage extension

### C7+ gate: NOW CONFORMS (was 8 violations)
Added 4 missing owl:Class declarations to address the 8 C7+ violations from v19.9.0:
- `reliability:Metric`, `reliability:Mitigation`, `reliability:Process` → in reliability_tbox
  (subClassOf reliability:ReliabilityConcept, all with skos:definition + dcterms:source).
- `risk:Mitigation` → in risk_tbox (subClassOf risk:RiskConcept).
Re-ran c7_plus_validator: **C7+ CONFORMS, 0 violations.**

### Cyclic subClassOf removed
`reliability:ReliabilityConcept rdfs:subClassOf reliability:ReliabilityConcept` (a literal self-loop)
removed; remaining parent is the correct `core:Concept`.

### File bumps (BP-D7)
- reliability_tbox v7.10.0 → **v7.11.0** (MINOR: 3 new classes + cycle fix; versionInfo=versionIRI=filename aligned).
- risk_tbox v3.1.0 → **v3.2.0** (MINOR: 1 new class).

### P4(b) — structural coverage extension (`redo_shacl_v4_1_0.ttl`)
3 cross-subject SHACL shapes (sh:Warning, advisory):
- S-COV-1: every owl:Class must have skos:definition.
- S-COV-2: every owl:Class must have dcterms:source.
- S-COV-3: every owl:NamedIndividual must have dcterms:source.
These apply across ALL v19 subjects via sh:targetClass owl:Class / owl:NamedIndividual.

### Honest scope on P4(b)
v3.1.0 adds STRUCTURAL coverage (the settled, evidence-supported part). Subject-specific SEMANTIC
shapes (e.g. "every Metric must declare measurementUnit", "every Lesson must have empiricalBasis")
remain a documented follow-up — they require per-subject ontology design that generic structural
rules cannot stand in for, and are not settled by the evidence available now (L-78 boundary).

### v19.9.0 → v19.10.0 (MINOR)
Additive: 4 new classes (reliability_tbox + risk_tbox), 1 new shapes file (redo_shacl_v4_1_0).
No class URIs removed/renamed; backwards-compatible. Cycle fix is a structural correction
(no vocabulary impact).

## v19.11.0 — Astrea-derived semantic coverage (P4b major fill, evidence-grounded)

### Test drive verdict: PASSES
Implemented core Astrea (Cimmino et al. 2020, ESWC) OWL2→SHACL mappings in Python (astrea_lite v1.0.0)
and ran across all 12 v19 subject TBoxes. Result: **1,250 NodeShapes mechanically derived** from
existing TBox axioms (rdfs:domain, rdfs:range, owl:Class, rdfs:isDefinedBy).

| TBox | classes | shapes | coverage notes |
|---|---|---|---|
| ae | 121 | 121 | 373 owl:disjointWith axioms (heaviest disjointness) |
| configuration | 104 | 104 | 42 domain + 40 range axioms |
| core | 17 | 17 | sparse - 19 disjointness only |
| knowledge_base | 231 | 231 | 92 disjointness, 29/31 domain/range |
| measurement | 67 | 67 | 26/25 domain/range; 0 violations vs full v19 data (genuinely clean) |
| meta | 95 | 95 | sparse axiomatization |
| oepack_release_history | 7 | 7 | 12 domain+range (high relative to class count) |
| performance | 7 | 7 | small subject |
| quality | 115 | 115 | 74/74 domain+range (well-axiomatized) |
| reliability | 334 | 334 | 234/226 domain/range, 41 disjointness; caught 7 real violations |
| risk | 82 | 82 | 36/35 domain/range |
| testing | 70 | 70 | 16/16 domain/range |
| **TOTAL** | **1,250** | **1,250** | |

### Validation runs (sample)
- measurement_shapes vs full v19 data: **conforms=True, 0 violations** (substantively clean —
  314+ usages of lowerBound, 247 appliesToRole, etc., all type-compliant).
- quality_shapes vs full v19 data: conforms=True, 0 violations.
- reliability_shapes vs full v19 data: **conforms=False, 7 violations** (real signal:
  type/class mismatches Astrea caught that hand-authored S-MEAS-2 couldn't see).
- Non-vacuousness check (reliability): 118/334 shapes have populated targetClasses in data
  (35%) — remaining 65% are reserved-capacity coverage, not defects.

### Honest coverage limits (Astrea cannot derive these without owl:Restriction axioms)
- Cardinality requirements ("Score MUST have a metric") — covered by hand-authored S-MEAS-2 only.
- v19 TBoxes contain **zero owl:Restriction axioms**, so the entire cardinality dimension is
  unreachable via Astrea. This is a real structural finding about the TBoxes themselves —
  enriching them with owl:Restriction would let Astrea derive S-MEAS-2-style shapes automatically.
  Flagged as a TBox-enrichment follow-up, not addressed in this release.

### Bundled files
- `02-shacl-safeguards/astrea_derived/<subject>_shapes_astrea_v1_0_0.ttl` × 12 (1,250 shapes total)
- `03-tooling/astrea_lite_v1_0_0.py` — the derivation tool itself, so consumers can regenerate
  the shapes after any TBox update.

### v19.10.0 → v19.11.0 (MINOR per BP-D7)
Additive: 12 new shape files + 1 tooling file. No class URIs touched. Backwards-compatible.

## v19.12.0 — TBox enrichment with owl:Restriction (P4b plan-step-2 executed)

### Triage audit findings (497 candidate cardinality decisions)
- Bucket A (universal BP-derived, e.g. skos:definition): 3,678 constraints across 1,226 classes,
  **already covered by S-COV-1/2/3 shapes** — kept at shape-layer per design choice (lower blast
  radius than dual encoding).
- Bucket B (subject-specific, 100%-usage signals): 36 candidate pairs.
- Bucket C (judgment-needed, needs domain authority): 364 pairs — deliberately deferred.

### L-65 honesty filter applied to bucket B (36 → 26 ENCODE, 10 DEFER)
Each of the 36 pairs evaluated against the test "is the property structurally inherent to the
class, or just empirically observed?" — 26 passed (encoded), 10 deferred. Full per-pair reasoning
in the build log; key examples:
- ENCODE: `SemVerVersion.semVerMajor/Minor/Patch` (SemVer requires them), `Score.value` (a score
  without a value is empty), `Bundle.hasBundleSHA256` (BP-D2 requires SHA verification),
  `ThresholdRow.appliesToMetric` (a row without a metric is meaningless).
- DEFER: `EngineeringTool.toolVersion` (tools can be unversioned), `Problem.hasResolutionOutcome`
  (open problems have no outcome yet — would be a sampling artifact).

### 26 owl:Restriction triples added across 8 TBoxes
| TBox | new restrictions | file bump |
|---|---|---|
| configuration_tbox | 4 | v2.3.4 → v2.4.0 |
| knowledge_base_tbox | 3 | v1.34.0 → v1.35.0 |
| measurement_tbox | 3 | v2.6.0 → v2.7.0 |
| oepack_release_history_tbox | 4 | v1.1.0 → v1.2.0 |
| performance_tbox | 2 | v1.4.0 → v1.5.0 |
| quality_tbox | 3 | v5.11.0 → v5.12.0 |
| reliability_tbox | 6 | v7.11.0 → v7.12.0 |
| risk_tbox | 1 | v3.2.0 → v3.3.0 |

### astrea_lite v1.0.0 → v1.1.0: M6 owl:Restriction mapping added
Implementation of the OWL2→SHACL mapping for owl:Restriction with owl:minCardinality / 
owl:maxCardinality → sh:minCount / sh:maxCount. Roundtrip verified: 26 owl:Restrictions in TBoxes
→ 26 sh:minCount constraints in derived shapes (perfect match).

### Validation against full v19 data: ZERO false positives
Re-ran derived shapes (v1.1.0) for all 5 affected subjects against full merged v19 data:
- measurement, quality, oepack_release_history, configuration: **conforms=True**, 0 violations.
- reliability: 7 violations (all pre-existing v1.0.0 type/class findings, NOT new cardinality ones).

This is the L-65 filter VINDICATED: the 26 pairs marked "structurally inherent" do in fact hold
100% in the data — the constraint is real, not metric-gamed.

### Bucket C status (deferred)
364 pairs needing domain authority remain untouched. Per termination criterion documented in plan:
reliability enrichment (largest bucket-C subject at 158 decisions) was not pursued — instead the
plan tackled bucket B first because its evidence was stronger and L-65-defensible. Bucket C remains
available for subject-by-subject pursuit when concrete need arises.

### v19.11.0 → v19.12.0 (MINOR per BP-D7)
Additive: 26 owl:Restriction triples in 8 TBoxes; astrea_lite v1.1.0; 12 regenerated derived shape
files. No class URIs removed/renamed; backwards-compatible.

## v19.13.0 — Close-out + R2 follow-up complete

### R2 follow-up
oepack_release_history_abox v1.12.0 → **v1.13.0** with 23 new orh:File_* release records covering
all files bumped/created across v19.9.0-v19.12.0 (Astrea-derived shapes, a reliability ontology v3.x cuts, TBox
enrichment bumps). Full provenance now recorded in the release history, mirroring the existing pattern.

### CLOSE_OUT.md
Single scoreboard authored in 04-documentation/, recording:
- 13 items closed
- 3 items genuinely deferred with L-78-honest reasoning per item (bucket C, v19 semantic suite
  extension, HermiT environment bridges).

### What "complete" means per L-78
Closing every item is not the same as completing the job. Per the lesson authored in v19.8.0,
completion means closing everything settled by convention/evidence and stating clearly which items
are genuinely deferred and why. Three deferrals remain, each genuinely requiring either domain
authority (bucket C) or environment changes (HermiT) — not more pack work.

### v19.12.0 → v19.13.0 (MINOR per BP-D7)
Additive: 23 release-history records; CLOSE_OUT.md docs. No class URIs touched.

## v20.0.0 — redo_shacl suite consolidated to a single file (MAJOR)

### Root-cause fix (beyond the governance request's symptom-fix)
The OE_RedoShaclSuite_Governance_Request flagged a severity/composition hazard across four shipped
redo_shacl files. Investigation (BP-D2) found the deeper cause: the four files were not four versions
of one artifact. v2_0_13_3 + v3_0_0 were the full 48-shape gate (two versions, one superseded); 
v3_1_0 (3 shapes) + v3_2_0 (4 shapes) were small coverage ADD-ONS mis-numbered as if they were newer
full-suite versions. The version numbering disguised a 4-shape add-on as "newer/more complete" than
the 48-shape gate — the real defect.

### Resolution: ONE file (redo_shacl_v4_1_0.ttl)
Merged the full v3.0.0 gate (48 shapes, C2 skos:definition at sh:Violation) with the genuinely-additive
add-on shapes (S-COV-2 dcterms:source, S-COV-3 individual source, S-MEAS-2 score-binds-metric) = 51
shapes in one self-contained file. Dropped S-COV-1 (the v3.1/v3.2 Warning-level class-definition rule)
as redundant-and-weaker: v3.0.0's C2 already covers it at Violation (L-66 — don't keep the advisory
twin of a blocking rule). Retired v2_0_13_3, v3_0_0, v3_1_0, v3_2_0.

### Decisions resolved (from the governance request)
- Composition: a single file eliminates the "which of four loads" hazard entirely — no owl:imports or
  manifest load-set declaration needed, because there is only one file.
- C2 severity: kept at sh:Violation (BP-D24 intent), per the recommended default.

### L-65 acceptance gate: PASS
Synthetic OE-namespace owl:Class lacking skos:definition, validated against redo_shacl_v4_1_0:
1 sh:Violation (correctly BLOCKS). No shipped file can be loaded such that this silently weakens —
there is only one file.

### Cross-session note (L-64)
The a domain ecosystem session independently pinned redo_shacl_v2_0_13_3 as canonical for ITS corpus. That is a
separate session's choice against its own copy and is unaffected by this OE-internal consolidation.
This change touches OE Pack artifacts only.

### v19.13.0 → v20.0.0 (MAJOR per BP-D7)
Breaking: 4 shape files removed, replaced by 1. Consumers referencing the old filenames must update
to redo_shacl_v4_1_0.ttl. README/INSTALL/release_check references updated.

## v20.1.0 — Package hygiene: oe_prov dedupe + redo_v2_5_18 merge (duplicate-version sweep)

### Trigger
Systematic scan (BP-D2) grouping every TTL by its declared ontology IRI, to find any other
redo_shacl-style multi-version situation. Result: NO other multi-version-of-one-file mess (the 11
tbox/abox/shacl groupings are legitimate distinct artifacts sharing a subject IRI). Two genuine
hygiene issues surfaced instead.

### Issue 1 — oe_prov shipped twice (RESOLVED, safe dedupe)
`oe_prov_v1_4_0.ttl` was byte-identical (SHA 73c66d0c…) in BOTH 01-ontologies/ and 05-prov-records/.
Removed the 01-ontologies/ copy; kept 05-prov-records/ (PROV ontology's semantic home). References are
to the oe-prov: namespace IRI, not a file path, so one physical copy suffices — no breakage.

### Issue 2 — redo_v2_5_18.ttl IRI-version collision (RESOLVED via merge, Option B)
redo_v2_5_18.ttl (10,600 triples, 365 classes) declared the <reliability> ontology IRI at versionInfo
2.5.12, colliding with reliability_tbox at 7.12.0 (same IRI, two versions). Investigation (BP-D2):
the 4 files "referencing" it do so only in rdfs:comment/dcterms:source PROSE (historical narration) —
NO owl:imports, no functional dependency. But it carried 124 UNIQUE live entities (103 classes + 15
properties + 6 other: the testing-method vocabulary — RegressionTestSuite, StressTest, SelfCheckGPT,
FaithfulnessScore, etc.) absent from the current reliability TBox.

Resolution (user ruling: Option B — merge + retire):
- Migrated the 124 unique entities (1,113 triples) into reliability_tbox via rdflib graph union.
- EXCLUDED the colliding ontology-header triples by construction (0 reliability-header triples in the
  add-set) — this is what resolves the version collision: the merged content lives under the single
  <reliability>@7.13.0 identity, no second version declaration.
- reliability_tbox v7.12.0 → **v7.13.0** (MINOR: +124 backwards-compatible entities).
- Retired redo_v2_5_18.ttl. Historical prose mentions in other files' comments kept as provenance.

### Verification (L-65 — the merge must be sound, per the authoring notes' HermiT-INCONSISTENT warning)
- First merge attempt BROKE the file (prefix-stripping bug → unbound ns2:). Caught by BP-D2 reparse,
  reverted, redone via rdflib graph union (correct prefix handling). Recorded honestly, not hidden.
- Merged tbox: parses (6,312 triples). Full 35-file ontology set parses (35,514 triples merged).
- C7+ gate on merged graph: CONFORMS, 0 violations (no undeclared types introduced).
- C2 check: 0 reliability classes lack skos:definition — the 124 migrated entities all carried their
  definitions, so they pass the strict v4.0.0 C2 gate.

### v20.0.0 → v20.1.0 (MINOR per BP-D7)
reliability_tbox +124 entities (MINOR); oe_prov dedupe + redo_v2_5_18 retirement (file-set reduction,
no vocabulary lost — all unique content migrated). No class URIs removed.

## v20.2.0 — Catalogue addition: 10 new lessons/BPs from combined conversation-analysis + a domain ecosystem proposal

### Ratification path
User ratified both: my own 5-lesson proposal (L-79..L-83, L-82 merged into L-65) AND a domain ecosystem's 7-candidate proposal (BP-X1, L-X2, L-X4..L-X7, L-X3 merged into BP-D47). Combined adds 1 new BP + 9 new Ls + 2 merges into existing entries.

### What was added (knowledge_base_abox_v1_35_0 → v1.36.0, MINOR)
From conversation-analysis proposal (mine):
- L-79 CitationTheaterDrift — citing a rule is a generation event, not a gate
- L-80 ContextAsKnowledgeConfusion — model can't distinguish read-this-turn from in-context
- L-81 SunkCostFoundationDrift — downstream stages treat upstream as confirmed by reference
- L-83 DisciplineDriftAcrossSessions — ceremony is per-action not per-session

From a domain ecosystem cross-session proposal:
- BP-X1 ConformanceClaimDisclosureDiscipline — '0 violations' claims must name shape version + method
- L-X2 RepeatedChallengeStopSignal — repeated user challenge under stable input = stop signal
- L-X4 ProbabilisticProposesDeterministicDisposes — compliant-checker architecture (reasoner+SHACL+verbatim triad)
- L-X5 HermeticAdversarialHarness — test paths must be package-relative
- L-X6 DispositionScopingDiscipline — disposition wording must scope precisely what is being retired
- L-X7 CrossSessionOwnershipDiscipline — propose, do not mutate; owning session decides versioning

### Merges (extension clauses, not replacements)
- L-65 VerifyBeforePublishing — extended with the L-82 internal-signal clause (fluency does not scale with ignorance; identifiers must trace by file-path-and-line)
- BP-D47 ConfidenceTierDisclosureDiscipline — extended with the L-X3 cross-LLM-laundering clause (LLM-only 'VERIFIED' demoted to CORROBORATED/TIER-B; only non-LLM authoritative resolution produces TIER-A)

### BP-D2 catch during authoring (recorded honestly per L-65)
First merge attempt broke the file: BP-D47's existing skos:definition used single-quote string delimiter, and my appended multi-line clause introduced literal newlines inside the single-quoted string. pyshacl parse failed at line 539. Fixed surgically: converted BP-D47's def from " to """ wrapping for multi-line content. Verified parse + all 10 new individuals present + both merges landed.

### Verification (L-65 — per the catalogue's own rule)
- ABox v1.36.0 parses (1,816 triples; was 1,725, delta +91).
- All 10 new individuals carry the full kb:Lesson/kb:BestPractice template (type, label, skos:definition, dcterms:source, rdfs:isDefinedBy, prov:generatedAtTime, prov:wasAttributedTo, prov:wasGeneratedBy).
- Both merges (L-82 into L-65, L-X3 into BP-D47) verified present in stored definitions.
- C7+ gate: 0 violations across the merged 34-file corpus (31,520 triples).
- redo_shacl_v4_1_0 full-run timed out (51 shapes × 31k triples × RDFS inference is heavy); per-individual template completeness was verified directly. The new entries are NamedIndividuals (not owl:Class), so C2 (skos:definition on owl:Class) does not target them; template-completeness is the relevant check.
- versionInfo=versionIRI=filename token all aligned at 1.36.0.

### Cross-session note
a domain ecosystem authored their proposal in their session and shipped it to OE; this OE session ratified and authored against OE's own ABox (within ownership). The merge of L-X3 into BP-D47 was the L-65-discipline-correct call against a domain ecosystem's own existing-coverage screening miss — recorded both in BP-D47's extension clause and in the analysis document. Per L-X7 (newly added), a domain ecosystem's proposal is now incorporated into OE's owned catalogue; if a domain ecosystem's session wants to reflect any of these new lessons into their own derived artifacts, that's their session's call.

### v20.1.0 → v20.2.0 (MINOR per BP-D7)
Additive vocabulary; no class URIs removed.

## v20.2.1 — Disclosure correction on the redo_shacl_v4_1_0 measurement (PATCH)

### Why this PATCH exists
The v20.2.0 validation entry framed template-completeness as equivalent to running redo_shacl_v4_1_0
on the new entries. That framing was wrong — exactly the L-79 citation-theater pattern, and exactly
what BP-X1 (newly added in v20.2.0) forbids. User correctly pushed back. This entry is the honest
re-measurement.

### The actual gate run (BP-X1-compliant disclosure)
Measurement: shape redo_shacl_v4_1_0; imports policy = no-imports single shape file;
corpus scope = full pack ontology corpus (01-ontologies/ + 05-prov-records/, 34 TTL files merged
to 31,520 triples); exclusions = none; inference = RDFS.

Result: **sh:Violation = 46 total. sh:Violation on the 10 newly-added entries + 2 merge targets = 0.**

### What the 46 are (honest disclosure)
All 46 violations are from shape S_MEAS_2_ScoreMustBindMetric (the hand-authored cardinality shape
merged from the old v3.2.0 add-on into the consolidated redo_shacl_v4_1_0). These are pre-existing
findings in the pack, not introduced by v20.2.0's catalogue additions. They reflect measurement:Score
individuals that lack a measurement:assessesMetric binding — a real existing data-quality gap,
unrelated to the lesson-catalogue change.

### Why the embedded validator reported 0 while SHACL reports 46
The two implementations measure DIFFERENT things, not the same thing disagreeing:
- c7_plus_validator_v1_0_0.py: implements ONLY C7+ TypeDeclarationShape. Reports 0 because no
  NamedIndividual references an undeclared type when the full pack is loaded.
- redo_shacl_v4_1_0 SHACL: implements all 51 shapes including S-MEAS-2. The 46 violations are all
  from S-MEAS-2, which the embedded validator does not implement.
Neither is wrong; they have different scopes. The C7+ "0 violations" claim under the embedded
validator was technically true (within its scope). What was missing was running the broader SHACL
suite to surface the S-MEAS-2 findings.

### L-66 self-application
Demoting redo_shacl_v4_1_0 from "passes" to "passes only on the new entries; 46 pre-existing
S-MEAS-2 findings remain in the pack" is the L-66 honest disposition. Any "0 violations" claim in
this report or in derived artifacts must henceforth name shape version, imports policy, corpus
scope, AND exclusions (per BP-X1 just authored).

### Disposition of the 46 pre-existing S-MEAS-2 violations
NOT FIXED in v20.2.1. This PATCH corrects DISCLOSURE only; the underlying data-quality findings
are a separate cleanup task (they exist in measurement:Score individuals across the pack and
require domain-authority decisions about which Score-to-Metric bindings are correct). Flagged for
a future MINOR/PATCH cycle.

### v20.2.0 → v20.2.1 (PATCH per BP-D7)
Pure documentation correction; no ontology content changed. Catalogue additions from v20.2.0
remain (10 new + 2 merges); they are genuinely clean under the corrected measurement.

## v20.3.0 — S-MEAS-2 migration: Score→Metric binding completed for derivable scores (MINOR)

### Root cause (established by version-history investigation)
The 46 S-MEAS-2 findings were the fingerprint of an incomplete migration. On 2026-05-19 17:30 the
oe_measurement_* subject was refactored to measurement_* at v1.0.0 (ORIGINATION per BP-D13). The
v19.4.0 Phase I1 design (quality_tbox v5.10.0 release note: "wired 14 quality dimensions to
operationalising metrics via 47 hasMetric triples") established the dimension→metric→score binding
intent, but the Score-INSTANCE-level oem:hasMetric binding was never propagated. The pack authored
the forward direction (Metric quality:hasScore Score) but not the inverse S-MEAS-2 checks
(Score oem:hasMetric Metric). User ruling: continue the migration.

### What was migrated (36 of 46)
For every Score with a forward quality:hasScore binding, the inverse oem:hasMetric triple was
authored by mechanical inversion (BP-D2: derived from the actual forward triples, not guessed; L-81:
no fabricated bindings). BP-D16 cross-check: oem:hasMetric has no declared domain/range, so
Score-as-subject is type-safe (no D-PHASE2-style domain-inference contradiction).
- 33 triples added to quality_abox v5.9.0 → v5.10.0 (the Template scores + their Metrics)
- 3 triples added to measurement_abox v2.7.2 → v2.7.3 (the OE_v15_4 StackMean scores)
- All 36 bindings unambiguous (each Score ← exactly 1 Metric; 0 multi-bound).

### What was NOT migrated (10 of 46) — honest disclosure
6 OEE scores (Score_oee_v3_0_0_OEE_*) + 4 reliability snapshots
(Snapshot_IssueResolutionRate_oepack_family_v17_*) could NOT be migrated mechanically: they carry NO
forward quality:hasScore binding to invert, AND no Metric individual exists for their implied metrics
(IssueResolutionRate, CQCount, CQResolutionCompleteness, CQSourceTraceability,
AlignmentDocumentationCompleteness, AlignmentRationaleCount, VersionHistoryDepth — all return NONE
when searched in the Metric population). Binding them would require AUTHORING 7 new Metric
individuals — new vocabulary, beyond "continue the migration", and an L-81 fabrication risk if the
metric IRIs were invented from score names. Deferred as a separate scoped decision (create the 7
Metric individuals, or accept these as prose-bound measurement records).

### Verification (L-65, BP-X1-compliant)
Measurement: shape redo_shacl_v4_1_0; imports policy = no-imports single shape file; corpus scope =
full pack ontology corpus (34 TTL files merged); exclusions = none; inference = RDFS.
Result: sh:Violation dropped from 46 → 10 (all 10 remaining are the non-derivable OEE/snapshot scores
above). The 36 migrated scores now pass S-MEAS-2.

### v20.2.1 → v20.3.0 (MINOR per BP-D7)
Additive: 36 oem:hasMetric triples. quality_abox v5.9.0→v5.10.0, measurement_abox v2.7.2→v2.7.3.
No class URIs removed; backwards-compatible.

## v20.4.0 — S-MEAS-2 migration COMPLETE: 7 Metric individuals created, all 46 findings resolved (MINOR)

### What was done (user ruling: create the 7 metrics, test-drive grounded)
Authored 7 new Metric individuals in quality_abox v5.10.0 → v5.11.0, bound the final 10 orphan scores
via oem:hasMetric (6 in measurement_abox v2.7.3 → v2.8.0, 4 snapshots in quality_abox). This completes
the v19.4.0 Phase I1 migration to the Score-instance level. S-MEAS-2: 10 → 0.

### Test-drive grounding (TEST_DRIVE_metric_measurements_v1_0_0)
Metric types and SPARQL implementations were grounded by ACTUALLY RUNNING the computations, not chosen
abstractly:
- Group A (computable, verified SPARQL authored):
  - I_IssueResolutionRate (oem:Metric, CritDim_Reliability) — verified 234/323=0.7245 on lifecycle ABox
  - I_OEE_CQCount (oem:CoverageMetric, CritDim_StructuralCharacteristic) — verified 35 CQs
  - I_OEE_VersionHistoryDepth (oem:SizeMetric, CritDim_Maintainability) — verified 156 priorVersion links
- Group B (external OEE v3.0.0 target absent; prose-defined, NO SPARQL per L-65):
  - I_OEE_AlignmentDocumentationCompleteness, I_OEE_AlignmentRationaleCount,
    I_OEE_CQResolutionCompleteness, I_OEE_CQSourceTraceability (all oem:Metric)

### Bonus integrity repair
The 4 IssueResolutionRate snapshots referenced quality:isScoreOf → I_IssueResolutionRate, which was a
DANGLING reference (zero triples). Creating I_IssueResolutionRate resolved that pre-existing dangling
reference in addition to the S-MEAS-2 binding.

### BP-D2 catch during authoring (recorded per L-65)
First authoring attempt used prefix "measurement:" which is not bound in quality_abox (the file binds
"oem:"). pyshacl parse failed. Reverted the bad append, re-authored with oem:. This is the third
single-vs-correct-prefix break this session — a recurring authoring-time pattern worth noting.

### Verification (L-65, BP-X1-compliant)
- Isolated S-MEAS-2 shape vs full corpus: sh:Violation = 0 (was 10, was 46 at v20.2.1).
- The 7 new metrics introduce 0 new violations under the redo_shacl_v4_1_0 suite (template-complete
  per BP-D42: definition + source + isDefinedBy; Group A also carry verified SPARQL + measuresCriterion).
- All files parse.

### v20.3.0 → v20.4.0 (MINOR per BP-D7)
Additive: 7 Metric individuals + 10 oem:hasMetric bindings. quality_abox v5.10.0→v5.11.0,
measurement_abox v2.7.3→v2.8.0. No class URIs removed.

### S-MEAS-2 finding history (closed)
v20.2.1: 46 (disclosed) → v20.3.0: 10 (36 derivable migrated) → v20.4.0: 0 (7 metrics created). COMPLETE.

## v20.5.0 — a domain ecosystem versioning-proposal assessment + non-blocking version-alignment gate (MINOR tooling)

### Cross-session assessment (L-X7 — analyze, do not mutate on their claims)
Assessed oepack-a domain ecosystem-to-oe-versioning-proposal-v1_0_0 (a domain ecosystem read OE v20.1.0; we are at v20.4.0).
Every finding independently re-verified against current files (BP-D2). Contamination audit clean: no OE
ontology mutated from a domain ecosystem claims; only OE-owned tooling added.

### P1 ACCEPTED (non-blocking)
verify_version_metadata_alignment_v1_0_0.py adopted into 03-tooling/; wired into release_check_v1.6.2 →
v1.6.3 as Gate K (informational/WARN, never blocks). Measurement (BP-X1): full 01-ontologies/ per-file
isolated parse, no merge — 25 OK, 3 MISMATCH, 2 NO_ONTOLOGY_DECL.

### NEW OE-owned finding surfaced (the real defect behind P1's symptom)
Release history records 6 a reliability ontology extension fragments as superseded by redo_v3_0_0.ttl, but redo_v3_0_0.ttl
does NOT exist on disk and the fragments are still present (2 without owl:Ontology headers, none imported,
classes unreferenced). The recorded consolidation was never completed — release history and filesystem
disagree. Documented in KNOWN_FINDINGS_v20_5_0.md as Finding 1; NOT auto-fixed (3-way resolution fork with
content-loss risk; requires author decision per L-78/L-81). This is OE-internal, surfaced via a domain ecosystem's gate.

### P2 FILED INFORMATIONAL / P3 MOSTLY CLOSED
P2 (L-78 recurrence): no ABox change (L-64 bleed avoidance). P3 (R6–R10): provisional codes already
ratified v20.2.0; residual content patterns need a separate handover with actual definitions.

### v20.4.0 → v20.5.0 (MINOR per BP-D7)
Tooling addition (gate script + release_check v1.6.3) + documentation (KNOWN_FINDINGS). No ontology
content changed; no S-MEAS-2 or other gate state altered.

## v20.6.0 — Finding 1 resolved: redo fragment cleanup completed (MINOR)

### Resolution (user ratified steps 1-3; step 4 under discussion)
The supplied redo_consolidation_completion_v1_0_0.zip was BP-D2 triple-verified: redo_v3_0_0.ttl genuinely
consolidates all 87 entities of the 5 stranded fragments, BUT 414/427 of its classes (incl. all 8 drift
classes) are ALREADY in the live reliability_tbox_v7_13_0. redo_v3_0_0 is a superseded intermediate
(reliability@3.0.0) forward-absorbed into reliability_tbox v7.x + risk_tbox v3.x. Adopting it would
reintroduce a same-IRI version collision. Resolution:

1. redo_v3_0_0.ttl + its README placed in 06-audit-artifacts/ (NOT in the live 01-ontologies set) — audit
   trail preserved, no IRI collision introduced.
2. Removed 6 absorbed fragment files from 01-ontologies/ (redo_v2_6_0_extensions,
   redo_v2_7_0_risk_and_problem_management, redo_v2_8_0_drift_taxonomy_extension,
   redo_v2_9_0_detection_attribution, redo_v2_10_0_issue_lifecycle,
   redo_v2_11_0_compliance_depth_taxonomy) — all verified absorbed into reliability_tbox before removal (L-81).
3. release_history v1.13.0 → v1.14.0: added File_redo_v3_0_0_ttl (audit-artifact status) + Sup_045/Sup_046
   completing the supersession chain (fragments → redo_v3_0_0 → reliability_tbox + risk_tbox). Existing
   fragment→redo_v3_0_0 records preserved (audit trail not rewritten, only completed).

### Verification (L-65, BP-X1-compliant)
- Gate K (verify_version_metadata_alignment): 24 files, 24 OK, 0 MISMATCH, 0 NO_ONTOLOGY_DECL (was 3+2 at
  v20.5.0). The a domain ecosystem-surfaced findings are fully cleared.
- Full corpus parses 28/28 (was 34; 6 fragments removed).
- S-MEAS-2 still 0 (fragment removal did not disturb the metric migration).

### OPEN (step 4, under discussion — NOT resolved in v20.6.0)
5 ITIL/KM classes from the redo_v2_7_0 fragment (KnowledgeArticle, KnowledgeBase, LessonsLearned, Playbook,
Runbook) are absent from the entire live corpus — not absorbed into reliability_tbox OR risk_tbox. Whether
they were intentionally dropped or lost in the reliability/risk split is an open content decision.

### v20.5.0 → v20.6.0 (MINOR per BP-D7)
Removed 6 superseded files; release_history MINOR bump; audit artifacts added. No live vocabulary lost
(all removed content verified present in reliability_tbox/risk_tbox).

## v20.7.0 — LessonsLearned consolidation (flat model) + scoped OE-reference scrub (MAJOR for kb)

### Model decision (user-ratified, test-drive grounded)
Adopted the FLAT model (Option A): a single canonical class kb:LessonsLearned whose 88 instances ARE the
lessons directly — no part-whole aggregate, no separate unit class, no membership property. Rationale
(user): prevents future drift of inventing another class as instance-of-Lesson, and simplifies algorithmic
processing. This matches how every other populated kb leaf (BestPractice 56, etc.) is modelled.

### What changed
- Authored kb:LessonsLearned (idiomatic plural; convention-admissible — plural class names already exist in
  kb, e.g. RequirementsAnalysis, UseCaseAnalysis; no naming-gate exception needed).
- Deprecated kb:LessonLearned (singular) and kb:Lesson: each marked owl:deprecated true +
  dcterms:isReplacedBy kb:LessonsLearned, retained as audit stubs (deprecate-not-delete discipline).
- Re-typed all 88 individuals (59 ex-LessonLearned + 29 ex-Lesson; disjoint sets, verified) to
  kb:LessonsLearned. Lossless.
- Retargeted 2 SHACL shapes: Shape_LessonLearnedAnnotationCompleteness -> Shape_LessonsLearned...; the
  lightweight Lesson_Shape -> LessonsLearned_LightShape. No instance loses coverage.

### Scoped OE-reference scrub (Category 1 only, user-ratified)
Removed 62 stale migration-provenance clauses " in Ontology Engineering v1.0.0..." from the two kb files,
keeping the "Migrated from rev:/redo:..." lineage intact (BP-D13 provenance preserved). Guarded against
collateral damage: bibliographic citations (Tudorache et al.; Domain-Specific Ontology Engineering),
methodology descriptions (Waterfall Ontology Engineering), and package-name decisions (oepack-family) were
explicitly preserved. Categories 2 (descriptive prose) and 3 (structural identifiers: oepack-release-history,
OEE metrics, OEPACK_Lesson IRIs) left untouched per scope.

### Verification (L-65, BP-X1-compliant)
- Full corpus parses 41/41.
- kb SHACL (v1.2.0): 0 violations — all 88 LessonsLearned pass annotation-completeness.
- Gate K: 24/24 OK, 0 MISMATCH.
- S-MEAS-2: 0 (unaffected).
- Scrub integrity: 0 residual "in Ontology Engineering v1.0.0"; Tudorache + oepack-family + Waterfall
  citations all preserved.
- Deprecation integrity: both old classes owl:deprecated + dcterms:isReplacedBy LessonsLearned.

### Versions (BP-D7)
kb_tbox v1.35.0 -> v2.0.0 (MAJOR: class deprecation+rename), kb_abox v1.36.0 -> v2.0.0 (MAJOR: 88 retyped),
kb_shacl v1.1.0 -> v1.2.0 (MINOR: shapes retargeted). Pack v20.6.0 -> v20.7.0.

### NOTE — still open (next)
The 4 remaining KM classes (KnowledgeArticle, KnowledgeBase, Playbook, Runbook) are NOT yet authored — they
were deferred pending this consolidation. They remain the last piece of the original Step-4 scope.

## v20.8.0 — Clean close: Step-4 KM-vocabulary disposition (MINOR, record-only)

### Decision
The 4 unauthored KM classes (KnowledgeArticle, KnowledgeBase, Playbook, Runbook) will NOT be added.
Verified findings (BP-D2 vs live v20.7.0): no live consumer; kb:KnowledgeBaseConcept is a taxonomic root
not a collection container; Playbook/Runbook are a genuine but unneeded gap. Authoring empty framework
classes is the L-71 anti-pattern; YAGNI until a concrete need. Definitions preserved in
06-audit-artifacts/redo_v3_0_0.ttl for verbatim retrieval if a need arises.

### Recorded as closed (L-48 guard)
ReleaseEvent_OEPack_v20_8_0 + ConsolidationStep_KM_Vocabulary_Disposition in the release-history ABox
(v1.14.0 -> v1.15.0) document the disposition so the audit-artifact classes are not re-discovered and
re-investigated. Reopen only on real future need.

### Deprecated stubs retained (deprecate-not-delete)
kb:LessonLearned / kb:Lesson remain owl:deprecated with dcterms:isReplacedBy kb:LessonsLearned; their
redirects stay live. No hard removal (the only unsafe direction).

### Arc closed
Finding 1 (redo_v3_0_0 consolidation, v20.6.0) -> LessonsLearned flat-consolidation + OE-reference scrub
(v20.7.0) -> KM-vocabulary disposition (v20.8.0, this record). All discussion threads from this session are
now resolved and recorded.

### Verification (L-65)
Full parse, Gate K, S-MEAS-2 re-checked below — all unchanged (record-only change).

### Versions (BP-D7)
release-history abox v1.14.0 -> v1.15.0 (MINOR, additive record). Pack v20.7.0 -> v20.8.0. No ontology
model change; no class/instance added or removed.

## v20.9.0 — Recorded this session's emergent lessons (MINOR)
Closing the gap that the user surfaced (and that newly-authored L-84 names): this session had applied
discipline for ~25 turns while recording zero lessons. Authored into knowledge_base_abox v2.0.0 -> v2.1.0
(88 -> 91 LessonsLearned), non-padded after duplicate-screen against 144 existing BP/Ls:
- L-84 record-lessons-as-they-emerge (a domain ecosystem proposal R, OE-internal grounding per L-64, cross-ref L-79; scoped to genuine lessons to avoid L-71 quota pressure).
- L-85 container-resets / no-automatic-persistence / session-start rehydrate+SHA-verify (cross-ref L-80).
- L-86 verify target-file prefix bindings + quote delimiters before hand-appending multi-line Turtle (distinct from rdflib-serialization L-46/L-53).
- MERGE: L-65 extended with verify-analytical-characterization-before-asserting (the twice-made KnowledgeBaseConcept / LeaderDecision lapses).
Rejected for OE: proposals O, P (scope-foreign PAMG-runtime concerns). Held: Q (no OE-internal instance yet).
Verification: parse 41/41, kb SHACL 0 (3 new lessons pass annotation-completeness), Gate K 24/24, S-MEAS-2 0.
Recorded in release-history v1.15.0 -> v1.16.0. Pack v20.8.0 -> v20.9.0.

## v20.10.0 — OE Operating Discipline v2.0.0 -> v2.1.0; doc now travels in the bundle (MINOR)
Updated the governance doc (OE-owned, authored directly, not a proposal) and placed it in 04-documentation
so it persists with the pack (L-85: the bundle is the only persistence path; a standalone doc is separately
fragile). Edits, each grounded in a recorded lesson:
- B5 (session-start rehydration, L-85): rehydrate + SHA-verify + ask-if-missing BEFORE the ceremony can run;
  the ceremony's step-2 verbatim extraction presupposes a loaded ABox.
- Session-close standing rule (L-84): record genuinely-emergent lessons before a release is complete, with
  the L-71 scope guard (not a quota).
- B3 sharpened (L-65 extension): decision-driving analytical characterizations are externally-verifiable
  claims; verify BEFORE asserting.
- Stale governance-source path corrected to knowledge_base_abox_v2_10_0.ttl.
- L-86 deliberately NOT elevated (within-artifact; caught by ceremony re-parse) — stays an ABox lesson.
Doc header Four->Five boundaries; v2.1.0 changelog note added. Pack v20.9.0 -> v20.10.0.

## v20.11.0 — L-84 session-sweep: 2 further emergent lessons (MINOR)
User honesty check: was L-84 applied to the whole session, or only the salient last turns? It was only the
salient ones. Performed the full session-close sweep. kb_abox v2.1.0 -> v2.2.0 (91 -> 93 LessonsLearned):
- L-87: a user-supplied "missing" file may be a superseded intermediate already forward-absorbed; verify
  overlap vs the live successor before adopting (the correct disposition can be archive-not-adopt). Ex: Finding-1.
- L-88: a scoped text-scrub requires exact-variant enumeration + keep-token guard. Ex: OE-reference scrub.
Deliberately NOT recorded (L-71 anti-padding): deprecate-not-delete (=L-57), test-drive-grounds-decision
(=BP-D2+L-78 application), found-file-archive-not-adopt (=consequence of L-87). Doc governance ref synced to
knowledge_base_abox_v2_10_0. Verified: parse 41/41, kb SHACL 0, Gate K 24/24, S-MEAS-2 0. Pack v20.10.0 -> v20.11.0.

## v20.12.0 — T1 ratified (Option A) + Score metric-link precision migration (coordinated MINOR)
Ratified Option A grounded in test-drive + provenance (ScoreClosedShape = self-labeled "typo prevention",
whitelist snapshotted v17.1.8 before oem:hasMetric existed -> stale, not a value-only ruling). Agreed semantics:
a score is meaningless without its producing metric, so the produced-by link is the score's DEFINING link and
must use the typed predicate. Actions:
- Migrated 42 Score-typed oem:hasMetric -> oem:derivedFromMetric (measurement_abox v2.8.0->v2.9.0: 9; quality_abox
  v5.11.0->v5.12.0: 33). 4 MeasurementSnapshot generics kept oem:hasMetric (not Scores; domain-correct).
- Extended redo_shacl S_MEAS_2 sh:or to accept derivedFromMetric (v4.0.0->v4.1.0).
- Widened ScoreClosedShape ignoredProperties: + derivedFromMetric + hasConfidenceTier (measurement_shacl v1.0.0->v1.1.0).
- Recorded L-89 (prefer purpose-built typed predicate over generic catch-all) — kb_abox v2.2.0->v2.3.0 (93->94).
Verified BOTH suites: measurement_shacl full-corpus no-inf 42->0; S-MEAS-2 0; fully-formed Score
(value+derivedFromMetric+tier) conforms; derivedFromMetric domain-clean; kb SHACL 0; Gate K 24/24.
RADAR tiered emission unblocked. Release-history v1.18.0. Pack v20.11.0->v20.12.0.

## v20.13.0 — T2/T3/T4 implemented + Option D ratified (coordinated MINOR)
RADAR submission v1.0.0, four governor-ruled items, each dry-run independently re-derived first.
- P-T2: + oem:Tier_D_HumanJudgment (measurement_abox v2.9.0->v2.10.0). Tier_D score: 0 viol.
- P-T3 (option a): + oem:MetricCategory + oem:inMetricCategory (measurement_tbox v2.7.0->v2.8.0); 6 categories
  seeded; ALL 19 metrics linked (incl. 5 quality:-namespace in quality_abox v5.12.0->v5.13.0). No L-71 gap.
- P-T4: + oem:DocumentMeasurementSubject; bindsArtifact/hasInputArtifact range -> core:Artifact;
  quality:OntologyArtifact re-parented under core:Artifact (quality_tbox v5.12.0->v5.13.0); 2 shape sh:class
  widened (measurement_shacl v1.1.0->v1.2.0). Document(core:Artifact) binding: 0 viol.
- Option D ratified: 04-documentation/OEM_RADAR_boundary_record_v1_0_0.md (OEE-authored governance record).
HONEST NOTE: RADAR's P-T4 "2 viol without re-parent" did not reproduce (pack has 0 artifact-binding instances;
RADAR's 2 were from its own emitted instances — scope difference). Re-parent still correct for future no-inf data.
Verified: parse 41/41, measurement_shacl 0, S-MEAS-2 0, Gate K 24/24, kb SHACL 0. Release-history v1.20.0. Pack v20.12.1->v20.13.0.
