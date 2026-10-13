# AI4SE ontology, edition 5.1.0

The ontology that accompanies the AI4X book series, volume 2 (AI for Software Engineering). It merges the 4.5 Enterprise concept hierarchy, the 5.0 enrichment modules, the version 1.0 modules and the Enhanced Complete specification into the three files the OE discipline requires: one T-Box, one A-Box, one SHACL file.

| Folder | Contents |
|---|---|
| `01-ontologies/` | `ai4se_tbox_v5_1_0.ttl` (classes, properties, modules) and `ai4se_abox_v5_1_0.ttl` (named individuals) |
| `02-shacl/` | `ai4se_shacl_v1_1_0.ttl` (the shapes) |
| `03-tooling/` | `ai4se_verify_v1_1_0.py` (measures the package), `ai4se_build_v1_1_0.py` (the consolidation, kept as a record), a negative fixture the shapes must reject |
| `04-documentation/` | the synthesis analysis, the findings register, the repair log, the quarantine register, the book-to-ontology mapping with its appended correction, the provenance archive |

## What is in it (measured on the files, 2026-10-13)

4,444 class resources (621 of them stubs, see the findings), 181 object properties, 187 datatype properties, 311 individuals (253 of them stubs), 29 source modules plus one module that holds the stubs. Every term keeps its original identifier; its module is its `dcterms:isPartOf` value.

## Verify it

```bash
pip install rdflib pyshacl
python3 -I 03-tooling/ai4se_verify_v1_1_0.py .
```

Every line must say PASS. The check parses the three files, counts the ontology headers (one each), validates the shapes, proves the shapes reject the known-bad fixture, and looks for terms that are used but not typed. A shape warning is not conformance: 3,951 classes have no definition yet, and the shapes report that as advisory.

## Read this before you rely on it

`04-documentation/FINDINGS_REGISTER_v1_0_2.md` states plainly what was wrong in the sources, what was repaired, what was moved out of the ontology and why, and what has not been checked. The ontology has not been run through an OWL reasoner.

## Curator, provenance and licence

Curated by Yusuf Altunel. This is an AI product: it was developed with various Claude models (Anthropic) under his curation. The licences are those of the OE Method: CC BY 4.0 for the ontology, shapes and documentation, Apache-2.0 for the tooling. See `LICENSE.md` and `CITATION.cff`.
