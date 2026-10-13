# Synthesis analysis, AI4SE ontology 5.1.0

Dated 2026-10-13. Every number was measured this session on the files in this package (verifier, build report, queries over the three files). Nothing is carried from an earlier summary.

## 1. What was synthesised

The first synthesis (5.0.x) consolidated 22 source files. A parallel session then deposited the 73 files it holds under `ai4se-sources/`, among them seven ontology files that 5.0.x did not cover: six version 1.0 modules (core foundation, infrastructure, lifecycle, practices, quality assurance, complete integration) and the Enhanced Complete specification. Edition 5.1.0 consolidates all 29 under the 3-file rule (BP-D54): one T-Box, one A-Box, one shapes file, each with exactly one ontology header. Each former source file is a module. `ai4se-sources/` was read, never modified.

## 2. Measured result

| | 5.0.1 | 5.1.0 |
|---|---|---|
| Source modules (incl. the stub module) | 23 | 30 (29 sources + stubs) |
| Class resources | 3,949 | 4,444 (4,431 named, 13 anonymous class expressions) |
| Object / datatype properties | 95 / 117 | 181 / 187 |
| Named individuals | 310 | 311 |
| Triples T-Box / A-Box / shapes | 28,553 / 2,042 / 62 | 32,762 / 3,217 / 158 |
| Quarantined triples | 6,656 | 6,858 |
| Classes without a definition (advisory) | 3,495 | 3,951 |

Namespaces in the package: `ai4se.org/ontology/v4#` (3,464 classes), `v5#` (485), the version 1.0 namespace (240), and five placeholder namespaces of the specification and its related files (`example.org/ai4se#` 84, `semanticweb.org/.../O4SE#` 69, `example.org/o4ai#` 47, `example.org/ontology-engineering#` 38, `example.org/ai4se/portfolio#` 4).

## 3. Findings on the new sources

1. **Two of the seven did not parse.** `AI4SE_Infrastructure_v1.0.ttl` and `AI4SE_Lifecycle_v1.0.ttl` each had one statement with no type predicate (`owl:SymmetricProperty .` and `owl:TransitiveProperty .`). The word `a` was restored; see `REPAIR_LOG_v1_0_1.tsv`. The other five parse as received.
2. **The specification is a second, parallel vocabulary.** It and its related files declare terms in placeholder `example.org` namespaces and carry 21 embedded verification queries. Renaming those identifiers into an `ai4se.org` namespace changes identifiers and is the owner's decision; it was not done.
3. **Embedded tests, executed once against the consolidated data (information, not conformance):** `query` literals (21): 2 ASK true, 6 ASK false, 12 SELECT with rows, 1 SELECT empty; 9 `hasTestQuery` literals cannot be run as written. A test that returns false states that the consolidated ontology does not yet contain what the specification claims it does; it is reported, not hidden.
4. **Two specification individuals violate the specification's own shapes.** `GitHubCopilot` and `SonarQubeAI` lack a required AI capability and SE process link (6 results). Shapes taken from sources are therefore carried at Warning severity, so the gate does not turn on the source's own data; the six results show in the warning count.
5. **Ten resources had no label** (one version 1.0 class and nine object properties in placeholder namespaces). A label was derived mechanically from the identifier (build report lists them).
6. **Self-scores and unsourced values** in the new sources were quarantined by the same rules as before: 202 more rows (to 6,858), nothing deleted.

## 4. Alignment with other ontologies (skos:closeMatch, never owl:equivalentClass)

A label match is evidence of similarity, not of identity.

- Internal, version 1.0 or specification term to a 4.x/5.x term, unique one-to-one label match: 9.
- To the O4SWE merged ontology, read only, unique label match: 383; 108 labels matched more than one term and were left unaligned; 30 terms the package uses from the O4SE namespace were aligned by local name.
- The 4.x/5.x bridges from 5.0.1 (11 `owl:equivalentClass`, same local name and label) are unchanged.

## 5. Conformance

`ai4se_verify_v1_1_0.py`: all PASS (three headers, no dangling term in any of the eight namespaces, T-Box/A-Box separation, shapes conform with zero violations, the known-bad fixture is rejected, quarantine register present). Structure check and manifest results are in the commit message record. Not done: no OWL reasoner run; no publish record; 3,951 classes still lack a definition.
