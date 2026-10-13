# Findings register, AI4SE ontology 5.1.0

Dated 2026-10-13. Replaces `FINDINGS_REGISTER_v1_0_1.md` (BP-D7). Measured on the files this session; the build report and the registers beside this file hold the rows. The analysis of the new sources is in `SYNTHESIS_ANALYSIS_v1_0_0.md`.

## 1. What was wrong in the files as received

Eight of the 29 source files did not parse as Turtle: the 4.5 Enterprise edition, five of the 21 generated files (the hybrid base, the phase 3 relationships file, the phase 2 multi-domain file, the phase 3 structural file, the domain engineering module), and two of the six version 1.0 modules (infrastructure, lifecycle). Earlier statements that the ontology was complete or at "100%" were made without parsing these files and cannot stand.

Repairs are mechanical and listed per file in `REPAIR_LOG_v1_0_1.tsv`: a mangled header restored (1 file), 1,477 truncated concept identifiers completed from the concept's own name, 1,650 unterminated labels closed, 77 uses of the invalid name Weights&Biases renamed WeightsAndBiases, 9 names split by a space or sign joined, 2 missing prefix declarations added, 2 missing type predicates restored. Truncated label numbers (for example "Technique 1") may be shortened and cannot be recovered.

## 2. What the ontology mostly consists of

Of the 3,585 classes the first 22 sources define, 3,131 (87%) carry a machine-generated identifier and 1,893 labels end in a running number such as "Architecture Analysis Technique 3". These are numbered technique placeholders, not described concepts. They are kept, as the owner's content. 3,951 of the 4,444 class resources have no definition.

## 3. What was moved out of the ontology (nothing was deleted)

6,858 triples are in `QUARANTINED_CLAIMS_v1_0_1.tsv` with module, subject, property, value and rule: template text repeated on twenty or more subjects (6,341), unsourced claims about named organisations, markets or cases (273), quoted figures with no source (153), self-assessments such as completeness or test-status values (91). The former headers' quality scores of 100 and 99 were never measured and were not carried.

## 4. What was added

- **Stubs:** 621 classes, 253 tool individuals and 65 properties are used in the sources but never defined. Each has a label derived from its identifier and a comment saying so, in the module "Referenced but undefined". Defining them is open work.
- **Derived labels:** 10 resources (1 class, 9 properties) had no label; a label was derived from the identifier.
- **Bridges and alignments:** 11 `owl:equivalentClass` bridges between 4.x and 5.x; `skos:closeMatch` alignments: 9 internal, 383 to O4SWE (read only), 30 by local name. 108 ambiguous label matches were not aligned.
- **Label conflicts:** terms with two labels keep the first as label, the other as alternative label.
- **Shapes from sources:** five shapes of the specification are carried at Warning severity; two of its own individuals violate them.

## 5. For the owner to decide

The specification and related files use placeholder `example.org` namespaces (five of them). Moving those identifiers into the package namespace changes identifiers; it was not done.

## 6. Not done, not checked

- No OWL reasoner has been run; logical consistency is unverified.
- The publisher of the OE discipline was not used (this session's GitHub access does not allow it): no publish record, no release tag.
- Executable tests embedded in the specification are run for information only; 6 ASK queries return false and 9 cannot be run as written.

## Change note, 5.1.0 (2026-10-13)

Adds the six version 1.0 modules and the Enhanced Complete specification as modules; retires the 5.0.1 T-Box, A-Box, shapes, build report, build script, quarantine register, repair log, provenance archive and verifier, each replaced under a new version token. Class shapes now apply to named classes only (anonymous class expressions are exempt). Licence, curator and provenance statements are unchanged from 5.0.1.

## Change note, 5.0.1 (2026-10-13), kept from the previous register

The owner ruled: the licences are those of the OE Method; his name stays as the curator; the work is an AI product developed with various Claude models. 5.0.1 added the curator, provenance statement and licence link to the headers, and `LICENSE.md` and `CITATION.cff`.
