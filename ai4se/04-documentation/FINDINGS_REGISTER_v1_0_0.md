# Findings register, AI4SE ontology 5.0.0

Dated 2026-10-13. Every number below was measured on the files this session; the build report (`BUILD_REPORT_v1_0_0.json`) and the registers beside this file hold the rows behind them.

## 1. What was wrong in the files as received

Six of the 22 source files did not parse as Turtle: the 4.5 Enterprise edition (the original upload) and five of the 21 generated files (the hybrid base, the phase 3 relationships file, the phase 2 multi-domain file, the phase 3 structural file and the domain engineering module). Earlier statements that the ontology was complete or at "100%" were made without parsing these files and cannot stand.

The repairs are mechanical and listed per file in `REPAIR_LOG_v1_0_0.tsv`: a mangled header restored (1 file), 1,477 truncated concept identifiers completed from the concept's own name, 1,650 unterminated labels closed, 77 uses of the invalid name Weights&Biases renamed WeightsAndBiases, 9 names split by a space or sign joined, and 2 missing prefix declarations added. Where a value had been cut off, it was completed only from something the file itself states; the truncated label numbers (for example "Technique 1") may be shortened and cannot be recovered.

## 2. What the ontology mostly consists of

Of the 3,585 classes that the sources actually define, 3,131 (87%) carry a machine-generated identifier and 1,893 labels end in a running number such as "Architecture Analysis Technique 3". These are numbered technique placeholders, not described concepts. They are kept, because they are the owner's content, but no one should read the figure "3,142 classes" as 3,142 described concepts. 3,495 of the 3,949 classes have no definition at all.

## 3. What was moved out of the ontology (nothing was deleted)

6,656 triples are in `QUARANTINED_CLAIMS_v1_0_0.tsv` with the module, the subject, the property, the value and the rule that moved them:

- **Template text (6,236):** a property and value that repeat on twenty or more subjects. 3,109 placeholder code snippets and 3,127 stock notes, all taken from five distinct texts. They carry no knowledge about the subject they sit on.
- **Unsourced claims (273):** 194 "fashion retail example" case texts that name real retailers, and facts or figures about named organisations or the Turkish market with no source (market relevance scores, adoption rates, cost ranges, accuracy ranges, visitor counts, founding years, compliance flags). The owner ruled earlier that cases without a verifiable source do not ship. One example of why: a founding year of 1998 was recorded for an e-commerce company in a file that names no source for it.
- **Quoted figures (137):** text that carries a percentage or an amount of money with no source.
- **Self-assessments (10):** counters and scores such as completeness values. The former ontology headers also carried quality scores of 100 and 99; they were never measured by any check and were not carried into the new headers.

## 4. What was added

- **Stubs:** 364 classes, 253 tool individuals and 14 properties were used in the sources but never defined. Each now has a label derived mechanically from its identifier and a comment saying so. They sit in their own module, "Referenced but undefined". Defining them properly is open work.
- **Bridges:** the sources use two namespaces (4.x and 5.x). Eleven classes exist in both with the same local name and the same label, and are joined by `owl:equivalentClass`. Other overlaps, if any, are not bridged.
- **Label conflicts:** four terms had two different labels in different files; the first (from the earlier module) is the label, the other is an alternative label.

## 5. Not done, not checked

- No OWL reasoner has been run, so logical consistency is unverified.
- The publisher of the OE discipline was not used for this repository (this session's GitHub access does not allow it), so there is no publish record and no release tag.
- The creator named in the sources does not match the owner's name, so the headers name "AI4SE Research Community" instead. The owner should set the attribution.
- The licence is not set.
- The book-to-ontology mapping carried a "100% alignment" headline that its own table contradicts; the correction is appended to it in `Book_Ontology_Comprehensive_Mapping_v1_0_0.md`.
