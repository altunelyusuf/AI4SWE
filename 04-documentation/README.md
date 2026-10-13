# OE Pack v20.8.0 — Complete Distribution

A complete, runnable ontology-engineering ecosystem for personal, academic, and industrial use.

## Layout
- `01-ontologies/` — the 25 v19.7.2 subject ontologies (TBox+ABox across 12 subjects: ae, configuration,
  core, knowledge_base, measurement, meta, performance, quality, reliability, risk, testing,
  oepack_release_history) + oe-prov + a reliability ontology core ontologies (redo_v2_5_18 … redo_v2_11_0).
  **measurement_tbox is v2.6.0** (GroundingScore/FactScore externally anchored + versionInfo realigned).
- `02-shacl-safeguards/` — per-subject SHACL shapes + the a reliability ontology C1–C8 gate shapes (redo_shacl_v4_1_0).
- `03-tooling/` — validate_with_imports (BP-D5 merged-imports validator), regression_suite.py,
  release_check (release gate script).
- `04-documentation/` — this README, INSTALL, validation report.
- `05-prov-records/` — PROV-O provenance.

## How to validate (BP-D5 merged-imports)
```
python3 03-tooling/validate_with_imports_v1_1_0.py \
  --data 01-ontologies/*.ttl --shapes 02-shacl-safeguards/<subject>_shacl_*.ttl \
  --imports-dir 01-ontologies --inference rdfs
```
Standalone SHACL on import-declaring files produces false positives (BP-D5); always merge imports.

## Provenance & version note (HONEST DISCLOSURE)
- The 37 ontology files are the SHA-verified v19.7.2 set you provided, with one change:
  measurement_tbox v1.4.0 → v2.6.0 (see validation report).
- The a reliability ontology safeguard suite + tooling are the highest versions on disk from THIS SESSION's v18-family
  build (redo_shacl_v4_1_0, validate_with_imports_v1_1_0, release_check_v1_6_2, regression_suite).
  They are v18-era; they run against the v19 ontologies but were authored in the v18 epoch. If a
  v19-matched a reliability ontology suite exists elsewhere, substitute it in 02-shacl-safeguards/ and 03-tooling/.
