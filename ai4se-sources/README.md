# AI4SE source files

Files of the AI for Software Engineering (AI4SE) book and ontology work, stored exactly as received
(byte for byte): nothing edited, repaired or renamed. This folder sits beside the OE Method copy that
was already in this repository; that copy is untouched.

`INVENTORY.tsv` lists every stored file with size, SHA-256 and a Turtle parse check.
`DUPLICATES.tsv` lists files that were received more than once and are stored only once (the
archives overlap heavily). `MANIFEST_SHA256.txt` verifies this folder from the repository root
(`sha256sum -c ai4se-sources/MANIFEST_SHA256.txt`).

| Folder | What it is | Status as received |
|---|---|---|
| `book-and-chapters/` | Chapter 2 "Software Development Lifecycle with AI4SE", its interactive page, three-phase AI4SDLC framework chapters, extension reports | Prose; AI-assisted drafts; references not verified |
| `ontology-enterprise-edition-v4.5/` | AI4SE Ontology v4.5 Enterprise Edition (3,142 class declarations) and release notes | Does not parse (header damaged, 1,160 garbled identifier lines); only 16 classes have a definition; duplicates present; no licence statement |
| `ontology-package-modules-and-phases/` | Nine modules including a 20-class Domain Engineering module, phase files, book mapping | Module files mostly parse; the Domain Engineering module has one syntax error; no licence statements |
| `ontology-v5-phases-*`, `book-ontology-integration*` | v5.0 hybrid base and phase files, integration reports, tool catalog, scripts | Hybrid base and relationships files do not parse; reported totals (3,142 classes) are not reflected in the files |
| `ontology-v1-modules/` | v1.0 modules with quality report | Four of six modules parse; Infrastructure and Lifecycle do not; quality scores are self-reported |
| `ontology-v5-specification/` | Enhanced Complete v5.0 specification (tests, glossary, enterprise extension) | Parses; 3 classes; licence statement CC BY 4.0 |

## Not yet done

No OE processing, repair or licence decision has been applied. Eight Turtle files do not parse as
received (see `INVENTORY.tsv`). The software engineering ontology files (O4SE, O4SDLC, domain
engineering) are kept in the O4SWE repository.
