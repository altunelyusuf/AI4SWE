# Structured research-and-fit-gap module documentation report — oe-method's 13 subject modules

Domain ontology for this run: each module's own shipped, generalised TBox/ABox under oe-method/01-vocabularies/. Same methodology as oe-pack's own module documentation, re-run here against oe-method's real bytes, not copied.

Found and fixed before this report could be produced: maturity_assessor_v1.1.0 and artifact_assessor_v2.1.0, tracked derived dependencies from oe-pack, hardcoded oe-pack's own directory names ('01-ontologies', '02-shacl-safeguards') and raised ZeroDivisionError against oe-method's real layout ('01-vocabularies', '02-safeguards'). Fixed at the root (VOCAB_DIR/SHAPES_DIR environment overrides, oe-pack v1.2.0/v2.2.0), re-derived into oe-method, verified genuinely portable.

Companion interactive HTML: `oemethod_modules_interactive_v1_0_0.html`, instantiated via rdodi-ecosystem's `08-brsf-corpus-template` mechanism (now at source v2.0.0) from `oemethod_modules_corpus_v1_0_0.json`.

## ae

**File:** `01-vocabularies/ae_tbox_v1_3_3.ttl` (owl:versionInfo "1.3.3", 6 prior version(s) on record)

**Mission:** Algorithm Efficiency answers: what will this cost as the input grows, and how do we know? It models asymptotic notation, analysis paradigms, algorithm families, input-size measures and the recurrence machinery for deriving bounds. It is software-engineering vocabulary, not ontology-engineering vocab

**Design:** 121 classes, 54 named individuals, 132 dcterms:source rationale triples.

**Maturity/capability:** level 5 Grounded (0-5 scale); capability 6/12, maturity 9/12 (0-12 dual scale).

**Fit-gap finding:** 103 of 121 declared classes (85%) have zero individuals in the shipped ABox.

## artifact_capability

**File:** `01-vocabularies/artifact_capability_tbox_v1_1_1.ttl` (owl:versionInfo "1.1.1", 2 prior version(s) on record)

**Mission:** Artifact capability and maturity answers two questions about an ONTOLOGY, not about the team that wrote it: what can this vocabulary do, and how settled is it? A reader comes here to compare two ontologies on properties of the artifacts themselves.

**Design:** 2 classes, 0 named individuals, 1 dcterms:source rationale triples.

**Maturity/capability:** level 2 Populated (0-5 scale); capability 3/12, maturity 6/12 (0-12 dual scale).

**Fit-gap finding:** no competency question or use-case class is declared (`que=0` on the maturity instrument).

## configuration

**File:** `01-vocabularies/configuration_tbox_v2_6_0.ttl` (owl:versionInfo "2.6.0", 8 prior version(s) on record)

**Mission:** Configuration answers: what is this artifact called, which version is current, and how would a stranger know? It holds naming conventions, version tokens, filename policies and the competency questions a package must be able to answer about itself. Its value is unglamorous and load-bearing: most gov

**Design:** 104 classes, 92 named individuals, 142 dcterms:source rationale triples.

**Maturity/capability:** level 4 Questioned (0-5 scale); capability 4/12, maturity 10/12 (0-12 dual scale).

**Fit-gap finding:** no competency question or use-case class is declared (`que=0` on the maturity instrument).

## core

**File:** `01-vocabularies/core_tbox_v1_8_0.ttl` (owl:versionInfo "1.8.0", 6 prior version(s) on record)

**Mission:** Core holds the primitives every other module depends on — Version, Process, Role, Metric, Concept — so that a version means the same thing in quality as in reliability. It is deliberately small: a shared vocabulary earns its place by being agreed, not by being comprehensive. A reader comes here when

**Design:** 18 classes, 3 named individuals, 25 dcterms:source rationale triples.

**Maturity/capability:** level 5 Grounded (0-5 scale); capability 5/12, maturity 8/12 (0-12 dual scale).

**Fit-gap finding:** 17 of 18 declared classes (94%) have zero individuals in the shipped ABox.

## knowledge_base

**File:** `01-vocabularies/knowledge_base_tbox_v2_3_0.ttl` (owl:versionInfo "2.3.0", 31 prior version(s) on record)

**Mission:** The knowledge base is the ecosystem's memory of what went wrong and what was done about it. It holds best practices and lessons, each carrying the evidence that produced it — not advice, but findings with provenance. A reader comes here before making a decision that someone has probably already got 

**Design:** 232 classes, 205 named individuals, 256 dcterms:source rationale triples.

**Maturity/capability:** level 5 Grounded (0-5 scale); capability 6/12, maturity 10/12 (0-12 dual scale).

**Fit-gap finding:** 227 of 232 declared classes (98%) have zero individuals in the shipped ABox.

## measurement

**File:** `01-vocabularies/measurement_tbox_v2_8_0.ttl` (owl:versionInfo "2.8.0", 12 prior version(s) on record)

**Mission:** Measurement answers: what number would settle this, and against what threshold? It holds metrics, thresholds, scores and observations, and it is the module that makes a quality claim arguable rather than assertable. Its distinguishing move is that an observation carries its method, so a figure can b

**Design:** 69 classes, 145 named individuals, 83 dcterms:source rationale triples.

**Maturity/capability:** level 5 Grounded (0-5 scale); capability 7/12, maturity 11/12 (0-12 dual scale).

**Fit-gap finding:** 61 of 69 declared classes (88%) have zero individuals in the shipped ABox.

## meta

**File:** `01-vocabularies/meta_tbox_v1_2_0.ttl` (owl:versionInfo "1.2.0", 4 prior version(s) on record)

**Mission:** Meta answers: what is an ontology made of, and how do two of them relate? It holds meta-modelling vocabulary — structure, alignment, mapping, the tool apparatus of editors and reasoners, and the SymbioticOntologyModel pattern. It is deliberately distinct from the knowledge base, which holds how-to k

**Design:** 95 classes, 19 named individuals, 100 dcterms:source rationale triples.

**Maturity/capability:** level 4 Questioned (0-5 scale); capability 4/12, maturity 8/12 (0-12 dual scale).

**Fit-gap finding:** no competency question or use-case class is declared (`que=0` on the maturity instrument).

## oepack_release_history

**File:** `01-vocabularies/oepack_release_history_tbox_v1_4_1.ttl` (owl:versionInfo "1.4.1", 3 prior version(s) on record)

**Mission:** Release history answers one question the other modules cannot: what actually happened? It records which file superseded which, in which release, on which date — the historical record, not the discipline that produced it and not the vocabulary that describes it. Its value appears when a claim about t

**Design:** 7 classes, 3 named individuals, 0 dcterms:source rationale triples.

**Maturity/capability:** level 3 Constrained (0-5 scale); capability 4/12, maturity 6/12 (0-12 dual scale).

**Fit-gap finding:** no competency question or use-case class is declared (`que=0` on the maturity instrument).

**Distinctive to this package:** oe-method's own copy carries only 3 individuals against oe-pack's 535. oe-method's release history was never meant to mirror oe-pack's session-specific event log — this is the honest, visible consequence of that scope choice, not a defect.

## performance

**File:** `01-vocabularies/performance_tbox_v1_6_0.ttl` (owl:versionInfo "1.6.0", 6 prior version(s) on record)

**Mission:** Performance answers: how does this behave under load, as distinct from how it scales in theory? It holds performance characteristics and the bridge to algorithm efficiency, keeping measured behaviour and asymptotic bound as separate claims that can disagree. It is small by design — most of the weigh

**Design:** 7 classes, 12 named individuals, 13 dcterms:source rationale triples.

**Maturity/capability:** level 4 Questioned (0-5 scale); capability 6/12, maturity 10/12 (0-12 dual scale).

**Fit-gap finding:** no competency question or use-case class is declared (`que=0` on the maturity instrument).

## quality

**File:** `01-vocabularies/quality_tbox_v5_14_1.ttl` (owl:versionInfo "5.14.1", 12 prior version(s) on record)

**Mission:** Quality answers: what would have to be true for this to be good enough, and who decided? It holds quality gates, the decisions they produce, the evidence those decisions rest on, assessment activities and the pitfalls that recur. Its distinguishing move is that a gate is modelled together with its c

**Design:** 115 classes, 444 named individuals, 192 dcterms:source rationale triples.

**Maturity/capability:** level 5 Grounded (0-5 scale); capability 8/12, maturity 12/12 (0-12 dual scale).

**Fit-gap finding:** 83 of 115 declared classes (72%) have zero individuals in the shipped ABox.

## reliability

**File:** `01-vocabularies/reliability_tbox_v7_13_2.ttl` (owl:versionInfo "7.13.2", 19 prior version(s) on record)

**Mission:** Reliability answers: how does this system fail, and would we notice? It holds failure modes, blind spots, verification modalities and degradation factors — and, unusually, the failure modes of the ENGINEERING PROCESS itself, including those specific to memoryless agents: parallel sessions forking a 

**Design:** 438 classes, 258 named individuals, 729 dcterms:source rationale triples.

**Maturity/capability:** level 5 Grounded (0-5 scale); capability 8/12, maturity 11/12 (0-12 dual scale).

**Fit-gap finding:** 330 of 438 declared classes (75%) have zero individuals in the shipped ABox.

## risk

**File:** `01-vocabularies/risk_tbox_v3_4_0.ttl` (owl:versionInfo "3.4.0", 7 prior version(s) on record)

**Mission:** Risk answers: what could go wrong, how badly, and what are we doing about it? It provides the FMEA pattern and the RiskItem pattern, consolidating risk vocabulary that was previously scattered across reliability, quality and core. It is distinct from reliability: reliability models how a system fail

**Design:** 82 classes, 42 named individuals, 53 dcterms:source rationale triples.

**Maturity/capability:** level 4 Questioned (0-5 scale); capability 4/12, maturity 9/12 (0-12 dual scale).

**Fit-gap finding:** no competency question or use-case class is declared (`que=0` on the maturity instrument).

## testing

**File:** `01-vocabularies/testing_tbox_v1_4_0.ttl` (owl:versionInfo "1.4.0", 3 prior version(s) on record)

**Mission:** Testing answers: what did we check, and could the check have failed? It holds testing methodology and test types in two parallel hierarchies — process and artifact — separated deliberately from reliability in 2026, because how a system fails and how you look for failure are different subjects. Its m

**Design:** 70 classes, 4 named individuals, 78 dcterms:source rationale triples.

**Maturity/capability:** level 5 Grounded (0-5 scale); capability 7/12, maturity 8/12 (0-12 dual scale).

**Fit-gap finding:** 66 of 70 declared classes (94%) have zero individuals in the shipped ABox.
