# Ontology Registration & Conformance Protocol (ORCP) v1.1.0

**Pack:** v20.78.0 · **Status:** governed procedure. The repeatable, ontology-agnostic process by which ANY
component (RADAR, a domain ecosystem, PAMG, O4SDLC, HUB/an integration blueprint, or a future one) registers with and/or conforms to the OEE
ecosystem. Distilled from the RADAR and a domain ecosystem rounds, including their failure modes.
**Authoritative companions:** `OEE_Component_Compliance_Strategy_v1_2_0.md` (the per-facet contract),
`OEM_RADAR_boundary_record_v1_0_0.md` (roles/guardrails), `OE_Operating_Discipline` (the BP/L rules).
This protocol orchestrates those; if it conflicts with them or with the disk, they win (BP-D2).

> **What this is for:** registration/conformance is a *cross-session, two-party* dance — a registrant (one
> session) and OEE (this session). Every prior round re-improvised it; this protocol makes it identical and
> auditable for every registrant.

---

## 0. Roles (who does what — never blurred)
- **Registrant** (RADAR/a domain ecosystem/PAMG/O4SDLC/HUB/…): identifies what it produces or must satisfy; emits
  conformant instances; PROPOSES gaps. Never mints OEE vocabulary, never edits OEE artifacts (B1/L-64).
- **OEE** (governance): re-derives every registrant claim against the live pack; RATIFIES; implements in OEE's
  own files; returns the exact contract. Owns the vocabulary and the decision (L-X7).

---

## 1. The protocol — 7 phases

### Phase A — Registrant: SELF-CLASSIFY against the recorded roster
The registrant reads `OEE_Component_Compliance_Strategy` §2 (the facetRole table) and decides, per facet,
which relationship(s) apply to *it*: registration (it deposits data), conformance (it must pass a gate),
both, or none. Output: a per-facet intent list. (It does NOT assume the 6-or-12 question — the recorded
roster is authoritative; 12 live facets.)

### Phase B — Registrant: EMIT a submission bundle
For each registration facet, the registrant emits OEM-conformant instances using the §3 hooks (e.g.
`oem:bindsArtifact`, `risk:assessesArtifact`, `performance:measuresArtifact`, …, all → `core:Artifact`).
For each conformance facet, it declares `core:hasCriticalityProfile` and ensures its data meets the gate at
that profile. The bundle MUST include: (1) the emitted TTL, (2) a builder/script, (3) a SHA-manifest of every
file, (4) a fit-gap note stating what it claims and any gap it found. **Scope disclosure (BP-X1):** the note
names the validation config used (inference on/off, which shapes, corpus scope).

### Phase C — OEE: GATE the submission (verify before trusting — "provenance is a claim")
On receipt, OEE, in THIS order (fail-stop on any step):
1. **B5/L-85** — verify the working tree vs the current MANIFEST (SHA), reinstall toolchain.
2. **SHA-verify** every submitted file against the registrant's manifest.
3. **Re-derive every dry-run/claim independently** against the live pack — do NOT accept the registrant's
   numbers. (RADAR's "2 violations" and "327 vs 42" both failed re-derivation; catch these here.)
4. **Validate the emitted instances** against EACH relevant facet's OWN SHACL (L-90 — not only the suites OEE
   is editing), at the correct config per facet (e.g. measurement_shacl is **no-inference**, BP-X1).
5. Confirm the registrant minted nothing and edited no OEE artifact (B1/L-64).

### Phase D — OEE: ADJUDICATE gaps (propose → ratify)
If the registrant proposed a gap (missing hook/category/tier/subject-type/gate):
1. Confirm the gap is **genuine and non-duplicate** (search the pack; a similar-named thing may exist with
   different semantics — e.g. `core:SeverityLevel` ≠ a criticality profile; `risk:hasIdentifiedRisk` ≠ a
   forward assessment hook). Do NOT reuse a near-match that means something different (L-89 applies only to a
   true purpose-fit).
2. Surface any genuine FORK to the governor (e.g. domain choice, core-vs-facet-local) — don't pre-decide
   (L-X7). Test-drive alternatives where it settles the choice (the A/B method).
3. Implement in OEE's own files with **coordinated SemVer bumps** (BP-D7/D17) and validate.

### Phase E — OEE: RECONCILE prose to disk (the step that bit us)
Whenever a status/contract changes, update EVERY prose location that mirrors it in the SAME change — the
strategy doc's status table, §4, the blueprint, facetRoleStatus. A doc that records build-status is a claim
that rots (L-91). Then re-run the governing suite (L-90) so the doc, the status field, and the SHACL agree.

### Phase F — OEE: RETURN the exact contract
Author an `OEE_to_<REGISTRANT>_*` note stating: the decision; the corrections to the registrant's framing
(honestly — a domain ecosystem's "6 facets" and RADAR's framing were both corrected); the precise IRIs/hooks to use; what
is operational vs deferred; and the new pack SHA. Bundle the pack + the note + any changed doc.

### Phase G — Registrant: RE-EMIT against the returned contract & CONFIRM
The registrant links to the new central IRIs (no local stand-ins), re-validates, and returns a closure note.
OEE re-derives the closure (Phase C again, lightweight) and records the round in release-history.

---

## 2. Per-registrant intent (what each of the named four will exercise)
These are *external/parallel-session* registrants. Expected relationships from the recorded roster:
- **RADAR** — registration into measurement (bounded executor; emits MeasurementRun/Binding/Score). Boundary
  record already governs it. Likely also registers risk/performance findings it computes.
- **PAMG** — consumes measurements to GRADE; per the boundary it measures-never-grades-conflation is forbidden
  — PAMG registers grading outputs, conforms to quality/reliability gates; must NOT mint measurement vocab.
- **O4SDLC** — an SDLC ontology; likely registers across configuration (version/change), testing, risk,
  knowledge_base, and conforms to quality/reliability. Strong "both"-heavy profile. (Not yet in pack.)
- **HUB / an integration blueprint** — the integration hub/blueprint; registers release-history lineage + conforms to core;
  may be the aggregation point that consumes others' registrations. Two rounds closed: round one
  (Profile_Standard, criticality-only, oe-pack v20.23.4) and round two (Profile_High, full facet
  registration across risk/testing/performance/configuration, oe-pack v20.78.0). Remains an accepted
  external registrant, not a governed roster subject.
Each runs the SAME Phases A–G; the only variation is which facets from §2 they touch.

## 3. Invariants (true for every registrant, every round)
1. Registrant proposes; OEE ratifies and owns the files (L-X7, B1/L-64).
2. OEE re-derives every claim; provenance is a claim (BP-D2).
3. Validate each facet's OWN governing suite at its correct config (L-90, BP-X1).
4. Never mint a near-match; never fabricate data to clear a check (L-57/L-65/L-89).
5. Coordinated SemVer on every artifact change (BP-D7/D17); status-prose synced to status fields (L-91).
6. Record every round in release-history; surface forks, don't manufacture them (L-78).

## 4. Honest scope note
This protocol is *procedure*, not new vocabulary — it orchestrates the existing contract. It does NOT itself
make any registrant "registered"; each must run Phases A–G. O4SDLC is not yet in the pack; its
first action is Phase A against the recorded roster. an integration blueprint has closed two rounds (see §2).
