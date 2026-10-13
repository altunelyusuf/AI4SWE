# Facet-Role Extension Blueprint v1.0.0
**Pack:** v20.17.0 · **Purpose:** the deferred build-work implied by the recorded facetRole/facetRoleStatus
classification, so non-`operational` roles are not forgotten. This is a roadmap, NOT an implementation.

## Recorded classification (v20.17.0, ratified)
8 both / 1 registration / 1 conformance / 2 internal. Each live SubjectOntology carries `orh:facetRole`
+ `orh:facetRoleStatus`. Items below are everything not yet `operational`.

## EXT-1 — Registration hooks — DONE in v20.18.0 (all four authored, validated end-to-end)
A subject-link object property (range `core:Artifact`, modeled on `measurement:bindsArtifact` /
`quality:assessesArtifact`), so a component can deposit its own data:
- **risk** (partial): add `risk:assessesArtifact` (domain `RiskAssessment` → `core:Artifact`); decision A3 pending
  — keep + widen `risk:hasIdentifiedRisk` domain `OntologyArtifact`→`core:Artifact` (test-drive for L-48 clash first).
- **performance** (intended): add `performance:measuresArtifact` (domain `PerformanceTest` → `core:Artifact`). No hook today.
- **configuration** (partial): add `configuration:appliesToArtifact` (domain `ChangeOperation` → `core:Artifact`).
- **testing** (intended): add a test→artifact hook, e.g. `testing:testsArtifact` (domain a Test class → `core:Artifact`). None today.

## EXT-2 — Conformance gates (status: intended/partial → operational)
Process-completeness gates, **case/criticality-parameterized** (per the risk discussion: gate the discipline of
doing it, not the result values). Requires (a) a case/criticality-profile notion, (b) per-profile completeness
conditions, (c) profile-parameterized SHACL.
- **testing** (intended): a "must-pass" gate — no `TestGate` / required-passed-acceptance-test exists today.
- **performance** (intended): performance-testing-completeness gate for the declared case.
- **risk** (partial): risk-management-completeness gate (every risk mitigated, every dimension assessed), case-parameterized.
- **OPEN DESIGN DECISION:** is the case/criticality profile a `core:`-level cross-cutting concept (risk, performance,
  reliability all parameterize by it) or facet-local? Deferred to the generalization/strategy work (piece 1).

## EXT-3 — measurement conformance nuance
measurement is `both/operational`, but its conformance role is **provider-of-criteria** (it defines/holds the
threshold rows) rather than **enforcer** (quality/reliability consume scores and gate). If a finer role model is
wanted, split "provides-criteria" vs "enforces-gate". Low priority; noted so it isn't lost.

## Carried from earlier
- **F-RH1**: 8 pre-existing release-history SHACL violations (deferred PATCH).
- **Artifact-umbrella**: `core#Artifact` vs `reliability#Artifact` duplicate (deferred reconciliation).


## v20.18.0 update
EXT-1 COMPLETE: risk:assessesArtifact (+ hasIdentifiedRisk domain widened to core:Artifact, A3), performance:measuresArtifact, configuration:appliesToArtifact, testing:testsArtifact — all range core:Artifact, each validated by its own SHACL (L-90) and end-to-end (a registrant instance validates 0). facetRoleStatus for risk/performance/configuration/testing updated to 'partial' (registration hook live; conformance GATE still EXT-2). EXT-2 (case-parameterized conformance gates) remains the open build. Note (for EXT-2): performance already enforces label/definition completeness on PerformanceTest — a model for gate design.


## v20.20.0 update — EXT-2 PILOT (risk) done
Core layer: minted core:CriticalityProfile (4 ordinal profiles Low/Standard/High/Critical) + core:hasCriticalityProfile (core:Artifact->CriticalityProfile). Verified core:SeverityLevel was the WRONG concept to reuse (it rates a finding/defect's impact, not a component's case) — minted distinct, not reused. Risk layer: risk:RiskManagementCompletenessGate (SHACL, profile-parameterized): at High/Critical, every identified risk must carry a mitigation or treatment; Low/Standard not gated. Test-driven: Critical+unmitigated FAILS, Critical+mitigated PASSES, Low+unmitigated PASSES. risk facetRoleStatus partial->operational (reg hook + gate both live). REMAINING EXT-2: replicate the profile-parameterized gate pattern for performance, testing, configuration (templates off risk).


## v20.21.0 — EXT-2 COMPLETE (all 4 facets)
performance/testing/configuration gates built on the risk template (profile-parameterized, High/Critical). testing+configuration each required a small completeness-linking property first (hasTestResult, satisfiesAcceptanceCriterion) — existing result/acceptance classes were unlinked; wired them rather than invent concepts. All 6 dual-faceted facets now operational on both axes. EXT-2 closed. Remaining backlog: F-RH1 (8 RH violations), Artifact-umbrella duplicate, ae/meta revisable classification.


## v20.23.3 observation (one-liner, not yet actioned)
EXT-2 gates check completeness of REGISTERED items, not PRESENCE of process: a High/Critical component that registers zero risk/perf/test/config items passes all four gates vacuously (verified on an integration blueprint round). If OEE ever wants criticality to MANDATE that High/Critical components actually DID risk/test/etc. work (a presence-gate, not just a completeness-gate), that is a future EXT — flagged, not built.
