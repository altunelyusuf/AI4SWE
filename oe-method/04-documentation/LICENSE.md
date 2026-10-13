# OE Pack v17.2.0 — License

**Copyright © 2026 the method author and contributors.**

---

## Terms of use

This package is provided for **academic research, industrial application, and open-source development** under the following terms:

### Permitted uses

✅ **Academic use** — citation in research papers, theses, dissertations; teaching at any educational institution; reproducing in coursework
✅ **Industrial use** — adoption in enterprise ontology engineering practice; integration into proprietary CI/CD pipelines; reference in internal documentation
✅ **Derivative works** — extending the discipline catalogue, adding new BestPractices, deriving new ontologies that import from this package
✅ **Redistribution** — sharing the unmodified package with attribution

### Required attribution

When citing or redistributing, include:

> "OE Pack v17.1.3 — the method author et al. 2026, integrated 3-phase remediation cycle plus 12-discipline working framework."

For academic citation, use the format in `README.md §Citation`.

### What's expected

- **Honest disclosure** — if you find a defect (e.g., SHACL violation, HermiT inconsistency), document it in your derivative work the way `Honest_Status_Analysis §7` documents this session's findings
- **Provenance preservation** — derivative works should preserve PROV-O records (in `10-prov-records/`) and add their own
- **Discipline propagation** — if you adopt the 12 BPs, encode any new BPs you derive as machine-queryable RDF following the same pattern (rather than only narrative documentation)

### Disclaimers

- This package is provided **as-is**, without warranty of fitness for any particular purpose
- HermiT-CONSISTENT verification is for the integrated bundle as shipped; substituting different versions of any ontology may produce different verdicts
- The discipline catalogue (BP-D1..BP-D12) is empirically grounded but not formally proven complete; new failure modes may emerge in your context
- pyshacl version compatibility may affect full v17 safeguard suite execution (see `INSTALL.md §Troubleshooting`)

### License compatibility

The included files retain their original licensing where applicable:
- HermiT 1.3.8 (referenced via `owlready2`): LGPL-2.1
- pyshacl: Apache-2.0
- rdflib: BSD-3-Clause
- W3C standards (OWL, RDF, SHACL, PROV-O): W3C Document License

The package's own contributions (PATCHes, discipline catalogue, tooling, documentation) are released under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

---

**Effective date:** 2026-05-09
**Document version:** v1.0.0
