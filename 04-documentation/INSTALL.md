# OE Pack v20.8.0 — Installation and Replication Guide

**For:** Industrial users, academic researchers, CI integration

---

## Prerequisites

- **Java 11+** (for HermiT 1.3.8 reasoner — included with `owlready2` Python package)
- **Python 3.10+**
- **rdflib 7.0+**, **pyshacl 0.31+** (for SHACL validation)
- **bash 4.0+** (for `release_check_v1_1_1.sh`)
- **unzip**, **sha256sum** (standard Unix utilities)

```bash
pip install rdflib==7.6 pyshacl==0.31 owlready2
```

HermiT is included in the `owlready2` package at: `<site-packages>/owlready2/hermit/HermiT.jar`

---

## Quick install

```bash
# 1. Extract the bundle
unzip oepack-family-v17_2_0.zip
cd oepack-family-v17_2_0

# 2. Verify integrity (BP-D8)
sha256sum -c MANIFEST_SHA256_oepack_final_v1_0_0.txt
# Expected: every file: OK

# 3. Make the release-check script executable (if not already)
chmod +x 08-tooling/release_check_v1_1_1.sh

# 4. Run the gate suite against this very bundle (dogfood)
bash 08-tooling/release_check_v1_1_1.sh \
  --zip ../oepack-family-v17_2_0.zip
```

---

## Full HermiT verification (replication)

To reproduce the "HermiT CONSISTENT at 32,744 triples" claim:

```bash
cd oepack-family-v17_2_0

# Use the bundled validation script
python3 08-tooling/validate_with_imports.py \
  --data 01-baseline-ontologies/*.ttl \
         02-i17-patches/*.ttl \
         03-phase1-deliverables/*.ttl \
         04-phase2-deliverables/oqc_*.ttl \
         04-phase2-deliverables/oepack_*.ttl \
         04-phase2-deliverables/phase2_*.ttl \
         04-phase2-deliverables/prov_*.ttl \
         05-phase3-deliverables/amod_*.ttl \
         05-phase3-deliverables/meta_*review_extension_v1_0_1*.ttl \
         05-phase3-deliverables/meta_*shape_interaction_v1_0_1*.ttl \
         05-phase3-deliverables/oepack_lessons*.ttl \
         05-phase3-deliverables/phase3_*.ttl \
         05-phase3-deliverables/prov_*.ttl \
         06-discipline-catalogue/*.ttl \
         10-prov-records/*.ttl \
  --shapes 07-shacl-shapes/oe_ecosystem_review_shapes_v1_0_0.ttl \
  --inference rdfs --advanced
# Expected output:
#   Violations: 0
#   Warnings:   0
```

For HermiT specifically (not via the wrapper):

```bash
# Step 1: merge OWL files only (NOT SHACL — those go in shapes path)
python3 - <<'PY'
from rdflib import Graph
from rdflib.namespace import OWL
import glob, os

SUPERSEDED = {'oqc_v2_2_5.ttl','redo_v2_5_18.ttl','meta_v6_5_0.ttl','amod_v1_2_6.ttl',
              'oqc_measurements_v17_v1_0_0.ttl','meta_v6_7_0_shape_interaction.ttl',
              'meta_v6_6_0_review_extension.ttl'}

g = Graph()
for cat in ['01-baseline-ontologies','02-i17-patches','03-phase1-deliverables',
            '04-phase2-deliverables','05-phase3-deliverables','06-discipline-catalogue',
            '10-prov-records']:
    for f in sorted(glob.glob(f"{cat}/*.ttl")):
        if os.path.basename(f) in SUPERSEDED: continue
        g.parse(f, format='turtle')

# Strip imports (per L-29)
out = Graph()
for t in g:
    if t[1] != OWL.imports: out.add(t)
out.serialize('/tmp/integrated.owl', format='application/rdf+xml', base='http://test/')
print(f'Total triples: {len(out):,}')
PY

# Step 2: run direct Java HermiT
java -Xmx4g -jar $(python3 -c "import owlready2,os; print(os.path.dirname(owlready2.__file__))")/hermit/HermiT.jar \
  --ignoreUnsupportedDatatypes \
  -k file:///tmp/integrated.owl
# Expected output: "<http://...> is satisfiable."
```

---

## SHACL R1-R8 verification (replication)

```bash
cd oepack-family-v17_2_0

python3 08-tooling/validate_with_imports.py \
  --data 01-baseline-ontologies/*.ttl 02-i17-patches/*.ttl \
         03-phase1-deliverables/*.ttl \
         04-phase2-deliverables/oqc_measurements_v17_v1_0_2.ttl \
         06-discipline-catalogue/*.ttl \
  --shapes 07-shacl-shapes/oe_ecosystem_review_shapes_v1_0_0.ttl \
  --inference rdfs --advanced

# Expected: Violations: 0, Warnings: 0
```

---

## CI integration

For GitHub Actions / GitLab CI / Jenkins:

```yaml
# .github/workflows/oepack-release.yml
- name: Verify OE Pack release
  run: |
    pip install rdflib pyshacl owlready2
    bash 08-tooling/release_check_v1_1_1.sh \
      --bundle 01-baseline-ontologies \
      --shapes 07-shacl-shapes \
      --validate-py 08-tooling/validate_with_imports.py
```

The script returns:
- `0` — All gates passed
- `1-7` — specific gate failure (see script header for codes)

---

## Bootstrap a fresh ontology engineering session

If you're starting new ontology work and want the 12-discipline framework pre-loaded:

```bash
cd oepack-family-v17_2_0

# Run the SPARQL self-test to verify the discipline catalogue loaded correctly
python3 08-tooling/oepack_bootstrap_sparql_kit_v1_0_0.py \
  --files 06-discipline-catalogue/oe_ecosystem_review_supplement_v1_0_4_1.ttl \
          06-discipline-catalogue/oe_ecosystem_review_discipline_extension_v1_0_5_5.ttl \
          06-discipline-catalogue/amod_v1_4_1_archive_extension.ttl \
  --query all
# Expected: all 6 queries return ≥ expected_min_rows; exit 0.

# Or query specific BPs:
python3 08-tooling/oepack_bootstrap_sparql_kit_v1_0_0.py \
  --files 06-discipline-catalogue/*.ttl \
  --query Q1_BestPractices --verbose
```

See `09-documentation/Bootstrap_HOWTO_v1_0_0.md` for the full procedure.

---

## Troubleshooting

### "HermiT INCONSISTENT" when adding the package to your existing graph

This is almost always caused by mixing SHACL shape files into the OWL graph. Check that:
1. SHACL files (containing `sh:NodeShape`, `sh:PropertyShape`) are in your validation pipeline, NOT your reasoning pipeline
2. You're using the PATCHED versions (from `02-i17-patches/` and Phase deliverables ending in `_v1_0_*.ttl`), not the original superseded versions

If the issue persists, re-run the bisection in `09-documentation/Honest_Status_Analysis_v1_0_0.md` against your loaded files to localize the conflict.

### "pyshacl KeyError 'this'" on the full v17 safeguard suite

Known pyshacl version compatibility issue with one SPARQL-based shape. Use only the `oe_ecosystem_review_shapes_v1_0_0.ttl` (R1-R8) for the canonical release gate. The v17 safeguards in `wpc_*.ttl` may require pyshacl ≥ 0.32 for full SPARQL-shape support.

### Filename does not match `amod:ProjectArchiveConvention`

Bundle names must match `^oepack-[a-z][a-z0-9_-]*-v\d+_\d+_\d+\.zip$`. If you derive new bundles, name them with 3-part SemVer in the suffix, not 4-part. The convention is documented in `06-discipline-catalogue/amod_v1_4_1_archive_extension.ttl`.

---

## What's verified vs what's claimed

| Claim | Verification source |
|---|---|
| HermiT CONSISTENT at 32,744 triples | This session's pre-bundle integration test (script in `09-documentation/Honest_Status_Analysis_v1_0_0.md`) |
| R1-R8 SHACL Conforms=True | This session's pyshacl 0.31 run |
| All filenames match AMOD conventions | `release_check_v1_1_1.sh` Gate D |
| All file SHA-256 hashes match manifest | `release_check_v1_1_1.sh` Gate E |
| 12 BPs + 7 lessons + 4 VFs queryable | `oepack_bootstrap_sparql_kit_v1_0_0.py --query Q6_BootstrapCheck` |

---

**End of INSTALL v1.0.0.**
