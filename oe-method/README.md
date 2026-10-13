# OE Method

A discipline for building ontologies that stay trustworthy across time, people and sessions.

**The problem it solves.** Ontology work is done in sittings, by people who forget, hand over, or
never meet. The usual failure is not a wrong axiom — it is a summary that drifts from the artifact,
a version token reused after an edit, a test that cannot fail, a claim nobody re-measured. Each is
invisible until it costs you.

**What is here.** The unit of the file structure is the package: one T-Box, one A-Box and one SHACL file, each with one ontology header; the former subjects are modules inside (BP-D54). The knowledge base and the other governance data are a unit of their own. To find the knowledge base without remembering a file name, run `python3 03-tooling/oe_resolve_v1_0_0.py . kb`.

| Directory | Contents | Licence |
|---|---|---|
| `01-vocabularies/` | The domain vocabularies as ONE T-Box and ONE A-Box (eleven and ten modules inside; one ontology header each) | CC BY 4.0 |
| `02-safeguards/` | The domain SHACL suites as ONE file (one module per suite) | CC BY 4.0 |
| `09-governance/` | The governance unit, with its own T-Box, A-Box and SHACL file (a unit of its own, version 1.0.0): the knowledge base (63 best practices and 146 lessons, as the integrity guard counts them, with their naming conventions, quality thresholds, metrics and blind spots), the release history, the publish-record shape and the OE Method backlog | CC BY 4.0 |
| `03-tooling/` | Release gates, integrity guards, publish and rehydrate tooling | Apache-2.0 |
| `04-documentation/` | The operating discipline and the registration protocol | CC BY 4.0 |
| `05-gates/` | Clean gate (no personal or project data) and completeness gate (no hollow vocabularies, no missing entry points), each with its proof | Apache-2.0 |
| `exemplar/` | A minimal package that has been through the protocol, gates green, SHACL proven to reject its own negative fixture | CC BY 4.0 |

**Start with** `04-documentation/GETTING_STARTED_v1_0_1.md` — one worked example, one sitting.
Then `HANDBOOK_v1_0_0.md` (why each rule exists), `DOCUMENT_TYPES_v1_0_0.md` (findings register,
close-out report, boundary record — with templates), `USE_CASES_v1_0_0.md` (is it worth it for you),
and `kb_explorer_v1_1_0.html` (all 175 rules, searchable — open it in a browser).
The method itself is `04-documentation/OE_Operating_Discipline_v2_17_1.md`.
The knowledge base is the accumulated evidence behind it.

## Core rules, in one breath

- Summaries state intent; the bytes govern. Re-derive before you repeat.
- A changed artifact gets a new version. Always.
- A gate never shown to fail verifies nothing.
- Resolve by highest version, never by a hard-coded name.
- Historical records are appended to, never rewritten. Generated artifacts are regenerated, never edited.
- Don't mint new structure on a single case; enrich what exists and wait for the second.

## Verify before you trust it

```bash
MF=$(ls MANIFEST_SHA256_v*.txt | sort -V | tail -1)
grep -v '^#' "$MF" | grep . | sed -E 's/[[:space:]]+\([0-9]+b\)[[:space:]]*$//' | sha256sum -c
python3 05-gates/oe_method_clean_gate_v1_7_0.py .
python3 05-gates/oe_method_completeness_gate_v1_2_0.py .
```

Every line `OK`, verdict `CLEAN`, verdict `COMPLETE`. Applying the method to itself is the point.

## What it costs

It is heavy for a single-file ontology. It assumes you are willing to be told you are wrong by a
script, and to record the times you were. If neither is true, the gates will feel like obstruction
rather than help. Said plainly here because a method that advertises itself as free is committing
the same error as a test that cannot fail.

## Provenance

Built by extraction from a working governance pack against an explicit keep-list — not by deleting
identifying data from a copy. Absence is therefore a property you can verify rather than a claim.
Evidence citations were generalised: the *kind* of case behind each lesson survives, the identity
of the project does not.
