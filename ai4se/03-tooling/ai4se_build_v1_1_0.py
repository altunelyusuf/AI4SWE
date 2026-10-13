#!/usr/bin/env python3
"""ai4se_build_v1_1_0.py -- consolidate the repaired AI4SE source files into the three canonical files.

Input : a folder with the repaired source Turtle files (one per former subject = module).
Output: <out>/01-ontologies/ai4se_tbox_v5_1_0.ttl, ai4se_abox_v5_1_0.ttl, <out>/02-shacl/ai4se_shacl_v1_1_0.ttl
        <out>/04-documentation/QUARANTINED_CLAIMS_v1_0_1.tsv, BUILD_REPORT_v1_1_0.json

Rules applied (every one is mechanical and counted in the report):
  Q1 template   a (property, string value) pair that repeats on >= 20 subjects is boilerplate, not knowledge
  Q2 unsourced  fixed property list: facts or figures about named organisations or markets, no source given
  Q3 selfscore  self-assessed quality scores and counters carried in the former headers
  Q4 figure     a string literal carrying a percentage or a currency amount (no source given)
  Quarantined triples are written to the register, never published in the three files.
Role split (BP-D54): classes, properties, restrictions, modules -> T-Box; individuals -> A-Box.
Stubs: a term used but never defined gets a labelled stub (label derived mechanically from its identifier).
"""
import sys, re, json, glob, os, collections
import rdflib
from rdflib import Graph, URIRef, Literal, BNode, Namespace, RDF, RDFS, OWL, XSD
from rdflib.namespace import DCTERMS, SKOS, SH
from rdflib.compare import to_canonical_graph

SRC, SRC2, OUT = sys.argv[1], sys.argv[2], sys.argv[3]      # repaired sources of the first synthesis, repaired new sources, output
O4SE = sys.argv[4] if len(sys.argv) > 4 else None             # optional: o4se_merged Turtle file, read only, for alignments
V4 = "http://ai4se.org/ontology/v4#"
V5 = "http://ai4se.org/ontology/v5#"
PKG = URIRef("http://ai4se.org/ontology/v5")
PKG_A = URIRef("http://ai4se.org/ontology/v5/abox")
PKG_S = URIRef("http://ai4se.org/ontology/v5/shacl")
MOD = "http://ai4se.org/ontology/v5/module/"

# ---- modules: (file name, module id, module IRI, human label) -----------------------------------
MODULES = [
 ("AI4SE_Ontology_v4_5_ENTERPRISE_EDITION.ttl", "EnterpriseBase", URIRef("http://ai4se.org/ontology/v4"), "Enterprise base: the 3,142-class edition 4.5 concept hierarchy with its technique classes and tools"),
 ("AI4SE_Ontology_v5_0_HYBRID_BASE.ttl", "HybridBase", URIRef(MOD+"HybridBase"), "Hybrid base: the first edition 5.0 classes and annotation properties for Turkish fashion retail and marketplace e-commerce"),
 ("AI4SE_Ontology_v5_0_PHASE2_ENRICHMENT.ttl", "Phase2Enrichment", URIRef(MOD+"Phase2Enrichment"), "Phase 2 enrichment: enriched classes for e-commerce platform engineering"),
 ("AI4SE_v5_Phase2_MultiDomain_Enrichment.ttl", "Phase2MultiDomain", URIRef(MOD+"Phase2MultiDomain"), "Phase 2 multi-domain enrichment: database, API, mobile and related engineering classes"),
 ("AI4SE_v5_Phase2_Security_Enrichment.ttl", "Phase2Security", URIRef(MOD+"Phase2Security"), "Phase 2 security enrichment: security engineering and security testing classes"),
 ("AI4SE_Ontology_v5_0_PHASE3_RELATIONSHIPS.ttl", "Phase3Relationships", URIRef(MOD+"Phase3Relationships"), "Phase 3 relationships: object properties and relationship restrictions between enriched classes"),
 ("AI4SE_v5_Phase3_Structural_Enhancement.ttl", "Phase3Structural", URIRef(MOD+"Phase3Structural"), "Phase 3 structural enhancement: structural properties and restrictions for the enriched classes"),
 ("AI4SE_Ontology_v5_0_PHASE7_ADVANCED_ENRICHMENT.ttl", "Phase7Advanced", URIRef(MOD+"Phase7Advanced"), "Phase 7 advanced enrichment: advanced retail and analytics classes"),
 ("AI4SE_Ontology_v5_0_PHASE11_FINAL_ENRICHMENT.ttl", "Phase11Final", URIRef(MOD+"Phase11Final"), "Phase 11 enrichment: further enriched classes"),
 ("AI4SE_Ontology_v5_0_PHASE12_ENTERPRISE_SYSTEMS.ttl", "Phase12EnterpriseSystems", URIRef(MOD+"Phase12EnterpriseSystems"), "Phase 12 enterprise systems: ERP, CRM, supply-chain and related system classes"),
 ("AI4SE_Ontology_v5_0_PHASE13_ADVANCED_TECH.ttl", "Phase13AdvancedTech", URIRef(MOD+"Phase13AdvancedTech"), "Phase 13 advanced technology: advanced technology classes"),
 ("AI4SE_Ontology_v5_0_PHASE14_SPECIALIZED_DOMAINS.ttl", "Phase14SpecializedDomains", URIRef(MOD+"Phase14SpecializedDomains"), "Phase 14 specialised domains: domain-specific engineering classes"),
 ("AI4SE_Ontology_v5_0_PHASE15_FINAL_100_PERCENT.ttl", "Phase15Final", URIRef(MOD+"Phase15Final"), "Phase 15 final enrichment: the last batch of enriched classes"),
 ("Ontology_Module_Architecture_Patterns.ttl", "ArchitecturePatterns", URIRef(V4+"ArchitecturePatternsModule"), "Architecture patterns: architectural styles, design patterns and their relations"),
 ("Ontology_Module_CICD_Automation.ttl", "CICDAutomation", URIRef(V4+"CICDAutomationModule"), "Continuous integration and delivery: pipeline, stage, deployment-strategy and tool classes"),
 ("Ontology_Module_Cloud_Containerization.ttl", "CloudContainerization", URIRef(V4+"CloudContainerizationModule"), "Cloud and containers: service models, orchestration and cloud-native classes"),
 ("Ontology_Module_Data_Engineering.ttl", "DataEngineering", URIRef(V4+"DataEngineeringModule"), "Data engineering: pipelines, storage, processing and data-quality classes"),
 ("Ontology_Module_DomainEngineering.ttl", "DomainEngineering", URIRef(V4+"DomainEngineeringModule"), "Domain engineering: domain analysis, domain modelling and ontology-engineering classes"),
 ("Ontology_Module_HybridSystems.ttl", "HybridSystems", URIRef(V4+"HybridSystemsModule"), "Hybrid systems: combinations of symbolic and statistical AI"),
 ("Ontology_Module_ROI_Metrics.ttl", "ROIMetrics", URIRef(V4+"ROIMetricsModule"), "Return on investment: cost, benefit and payback measures with scenario individuals"),
 ("Ontology_Module_SemanticTechnologies.ttl", "SemanticTechnologies", URIRef(V4+"SemanticTechnologiesModule"), "Semantic technologies: knowledge graphs, reasoners, query languages and serialisations"),
 ("Ontology_Module_TestingTaxonomy.ttl", "TestingTaxonomy", URIRef(V4+"TestingTaxonomyModule"), "Testing taxonomy: test levels, techniques and test tools"),
]
V1 = "http://www.semanticweb.org/ontologies/2025/AI4SE"
MODULES += [
 ("AI4SE_Core_Foundation_v1.0.ttl", "V1CoreFoundation", URIRef(V1), "Version 1.0 core foundation: AI-for-SE system taxonomy, integration patterns and AI capabilities, with competency questions"),
 ("AI4SE_Lifecycle_v1.0.ttl", "V1Lifecycle", URIRef(V1+"/Lifecycle"), "Version 1.0 lifecycle: AI-enhanced software lifecycle phases and their transitions"),
 ("AI4SE_Practices_v1.0.ttl", "V1Practices", URIRef(V1+"/Practices"), "Version 1.0 practices: AI-enhanced methodologies and engineering techniques"),
 ("AI4SE_Infrastructure_v1.0.ttl", "V1Infrastructure", URIRef(V1+"/Infrastructure"), "Version 1.0 infrastructure: AI-powered tools, platforms and services"),
 ("AI4SE_QualityAssurance_v1.0.ttl", "V1QualityAssurance", URIRef(V1+"/QualityAssurance"), "Version 1.0 quality assurance: quality dimensions, test cases and validation shapes"),
 ("AI4SE_Complete_Integration_v1.0.ttl", "V1CompleteIntegration", URIRef(V1+"/Complete"), "Version 1.0 integration: the integration entry point of the version 1.0 modules"),
 ("AI4SE_Ontology_Specification_AI4SE_Enhanced_Complete_v5_0.ttl", "V5Specification", URIRef("http://example.org/ai4se"), "Enhanced Complete specification: term definitions, requirements, competency questions and executable verification queries"),
]
STUB_MOD = ("ReferencedButUndefined", URIRef(MOD+"ReferencedButUndefined"),
            "Referenced but undefined terms: stubs for terms the source files use without ever defining them")

def local(u):
    s = str(u); return s.split("#")[-1] if "#" in s else s.rsplit("/", 1)[-1]

def human(idf):
    t = re.sub(r"[_]+", " ", idf)
    t = re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", t)
    return re.sub(r"\s+", " ", t).strip()

# ---- quarantine rules -------------------------------------------------------------------------
Q2_PROPS = {"fashionRetailExample", "monthlyVisitors", "foundedYear", "PCIDSSCompliant", "APIAvailable",
            "adoptionRate", "turkishMarketRelevance", "hasAccuracyRange", "hasTimeReduction", "costRange"}
Q3_PROPS = {"hasCorrectness", "hasCompleteness", "hasConsistency", "hasAdaptability", "hasUsability", "hasCapacity",
            "hasDeepness", "hasComprehensiveness", "hasOverallQuality", "hasDepthCoverage", "hasBreadthCoverage",
            "enrichmentPercentage", "numberOfClasses", "totalClassesBefore", "totalClassesAfter", "basicClasses",
            "enrichedClasses", "numberOfEnrichedClasses", "qualityFrameworkVersion", "numberOfTestCases",
            "hasTestSuite", "mergeDate", "mergeStrategy", "sourceOntology", "moduleVersion",
            # asserted results and scores in the version 1.0 and specification files
            "testStatus", "testResult", "dateExecuted", "dateLastRun", "testPassed", "validated", "verified", "hasScore",
            "evidencedBy", "hasQualityScore", "hasStatistic", "performanceMetric", "testCasesAdded", "accuracyScore"}
FIG = re.compile(r"\d+(\.\d+)?\s?%|[\$€₺£]\s?\d")
HEADER_PREDS = {DCTERMS.title, DCTERMS.description, DCTERMS.creator, DCTERMS.created, OWL.versionInfo, OWL.priorVersion,
                OWL.versionIRI, OWL.imports, RDFS.comment, RDFS.label, DCTERMS.license, DCTERMS.publisher,
                DCTERMS.modified, DCTERMS.contributor, DCTERMS.identifier, DCTERMS.isPartOf}
KEEP_FIG_PROPS = {"definition", "comment", "label", "prefLabel", "altLabel", "hasFormula", "scopeNote", "hasToolURL"}

# ---- load -------------------------------------------------------------------------------------
graphs = {}
for fn, mid, miri, mlabel in MODULES:
    p = os.path.join(SRC, fn); p = p if os.path.exists(p) else os.path.join(SRC2, fn)
    g = Graph(); g.parse(p, format="turtle"); graphs[mid] = g

# which subjects each module defines (named subjects only), before any header stripping
defined_in = collections.defaultdict(set)
header_nodes = {}
for mid, g in graphs.items():
    hn = set(g.subjects(RDF.type, OWL.Ontology)); header_nodes[mid] = hn
    for s in set(g.subjects()):
        if isinstance(s, URIRef) and s not in hn:
            defined_in[s].add(mid)

# ---- Q1: template pairs across the whole corpus ---------------------------------------------
pair_subjects = collections.defaultdict(set)
for mid, g in graphs.items():
    for s, p, o in g:
        if isinstance(o, Literal) and isinstance(s, URIRef) and not (p in (RDFS.label, SKOS.definition, RDFS.comment)):
            pair_subjects[(p, str(o))].add(s)
Q1_PAIRS = {k for k, v in pair_subjects.items() if len(v) >= 20}

quarantine = []   # (module, subject label, subject iri, property, value, rule)
def lab_of(g, s):
    for o in g.objects(s, RDFS.label): return str(o)
    return human(local(s))

clean = {}
for mid, g in graphs.items():
    c = Graph()
    hn = header_nodes[mid]
    for s, p, o in g:
        if s in hn: continue                       # header triples are replaced by the module resource
        pn = local(p)
        rule = None
        if isinstance(o, Literal):
            if (p, str(o)) in Q1_PAIRS: rule = "Q1 template"
            elif pn in Q2_PROPS: rule = "Q2 unsourced"
            elif pn in Q3_PROPS: rule = "Q3 selfscore"
            elif pn not in KEEP_FIG_PROPS and FIG.search(str(o)): rule = "Q4 figure"
        elif pn in Q3_PROPS: rule = "Q3 selfscore"
        if rule:
            quarantine.append((mid, lab_of(g, s) if not isinstance(s, BNode) else "(blank node)", str(s), str(p), str(o), rule))
            continue
        c.add((s, p, o))
    # blank nodes that lost every property but the type stay harmless; drop bnodes with no remaining content
    clean[mid] = c
    for pre, ns in g.namespaces(): pass

# the V4 / V5 prefixes and standard ones
def bind(g):
    g.bind("", Namespace(V4)); g.bind("v5", Namespace(V5)); g.bind("owl", OWL); g.bind("rdfs", RDFS)
    g.bind("xsd", XSD); g.bind("skos", SKOS); g.bind("dcterms", DCTERMS); g.bind("sh", SH); g.bind("rdf", RDF)
    return g

# ---- merge with module membership -----------------------------------------------------------
merged = Graph()
for mid, c in clean.items():
    for t in c: merged.add(t)

# label conflicts: first module (in MODULES order) wins rdfs:label, the others become skos:altLabel
order = [m[1] for m in MODULES]
seen_label = {}
for mid in order:
    for s, o in list(clean[mid].subject_objects(RDFS.label)):
        if not isinstance(s, URIRef): continue
        if s in seen_label and str(seen_label[s]) != str(o):
            merged.remove((s, RDFS.label, o)); merged.add((s, SKOS.altLabel, o))
        else:
            seen_label.setdefault(s, o)

# bridges between the two namespaces: same local name, both classes, labels equal after dropping a parenthesis
def norm(l): return re.sub(r"\s*\(.*?\)", "", l).strip().lower()
bridges = []
for c in list(merged.subjects(RDF.type, OWL.Class)):
    if isinstance(c, URIRef) and str(c).startswith(V4):
        c5 = URIRef(V5 + str(c)[len(V4):])
        if (c5, RDF.type, OWL.Class) in merged:
            l4 = [str(x) for x in merged.objects(c, RDFS.label)]; l5 = [str(x) for x in merged.objects(c5, RDFS.label)]
            if l4 and l5 and norm(l4[0]) == norm(l5[0]):
                merged.add((c, OWL.equivalentClass, c5)); bridges.append(local(c))

# ---- stubs --------------------------------------------------------------------------------
TOOL_PREDS = {"usesTool", "hasToolExample", "requiresTool", "implementedIn", "implementedBy", "integrates"}
typed = set(merged.subjects(RDF.type, None))
PKG_NS = (V4, V5, V1 + "#", "http://example.org/ai4se#", "http://example.org/ai4se/portfolio#",
          "http://www.semanticweb.org/ontologies/2025/O4SE#", "http://example.org/o4ai#", "http://example.org/ontology-engineering#")
def inpkg(x): return isinstance(x, URIRef) and str(x).startswith(PKG_NS)
ocount = collections.defaultdict(collections.Counter); used = set(); props_used = collections.defaultdict(lambda: [0, 0])
for s, p, o in merged:
    for x in (s, o):
        if inpkg(x): used.add(x)
    if inpkg(p):
        used.add(p); props_used[p][0 if isinstance(o, Literal) else 1] += 1
    if inpkg(o) and p not in (RDF.type,): ocount[o][local(p)] += 1
stub_classes, stub_tools, stub_props = [], [], []
STUB_COMMENT = "Stub declared by the package build: the source files use this term but never define it. The label is derived mechanically from the identifier."
for x in sorted(used, key=str):
    if x in typed: continue
    preds = ocount.get(x, collections.Counter())
    if x in props_used:
        lit, iri = props_used[x]
        merged.add((x, RDF.type, OWL.DatatypeProperty if iri == 0 else OWL.ObjectProperty if lit == 0 else RDF.Property))
        stub_props.append(local(x))
    elif preds and set(preds) <= TOOL_PREDS | {"hasToolExample"} or (preds and sum(preds[k] for k in preds if k in TOOL_PREDS) >= max(1, sum(preds.values()) // 2)):
        merged.add((x, RDF.type, OWL.NamedIndividual)); merged.add((x, RDF.type, URIRef(V4 + "Tool")))
        stub_tools.append(local(x))
    else:
        merged.add((x, RDF.type, OWL.Class)); stub_classes.append(local(x))
    merged.add((x, RDFS.label, Literal(human(local(x)), lang="en")))
    merged.add((x, RDFS.comment, Literal(STUB_COMMENT, lang="en")))
    defined_in[x].add("ReferencedButUndefined")

derived_labels = []
for ty in (OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.NamedIndividual):
    for x in set(merged.subjects(RDF.type, ty)):
        if isinstance(x, URIRef) and not (x, RDFS.label, None) in merged:
            merged.add((x, RDFS.label, Literal(human(local(x)), lang="en"))); derived_labels.append(str(x))
# ---- alignments (skos:closeMatch; a label match is evidence of similarity, not of identity) ----------
def key(l): return re.sub(r"[^a-z0-9]", "", re.sub(r"\(.*?\)", "", str(l).lower()))
def cls_by_key(g, pred):
    d = collections.defaultdict(set)
    for c in set(g.subjects(RDF.type, OWL.Class)):
        if isinstance(c, URIRef) and pred(c):
            for l in g.objects(c, RDFS.label):
                k = key(l)
                if len(k) >= 6 and not re.search(r"\d$", str(l).strip()): d[k].add(c)
    return d
core_ns = (V4, V5)
A_ = cls_by_key(merged, lambda c: str(c).startswith(core_ns)); B_ = cls_by_key(merged, lambda c: str(c).startswith((V1 + "#", "http://example.org/ai4se#")))
align_internal = 0
for k, bs in B_.items():
    if k in A_ and len(bs) == 1 and len(A_[k]) == 1:
        b, a = next(iter(bs)), next(iter(A_[k])); merged.add((b, SKOS.closeMatch, a)); align_internal += 1
align_o4se = 0; align_o4se_stub = 0; o4se_ambiguous = 0
if O4SE:
    og = Graph(); og.parse(O4SE, format="turtle")
    O_ = cls_by_key(og, lambda c: True)
    for k, cs in A_.items():
        if k in O_:
            if len(cs) == 1 and len(O_[k]) == 1:
                merged.add((next(iter(cs)), SKOS.closeMatch, next(iter(O_[k])))); align_o4se += 1
            else: o4se_ambiguous += 1
    byloc = collections.defaultdict(set)
    for c in set(og.subjects(RDF.type, OWL.Class)):
        if isinstance(c, URIRef): byloc[local(c)].add(c)
    O4B = "http://www.semanticweb.org/ontologies/2025/O4SE#"
    for x in sorted(used, key=str):
        if str(x).startswith(O4B) and len(byloc.get(local(x), ())) == 1:
            merged.add((x, SKOS.closeMatch, next(iter(byloc[local(x)])))); align_o4se_stub += 1

# ---- module resources ---------------------------------------------------------------------
mod_res = Graph()
member_count = collections.Counter()
for s, mods in defined_in.items():
    for m in mods: member_count[m] += 1
for fn, mid, miri, mlabel in MODULES + [(None,)+STUB_MOD]:
    mod_res.add((miri, DCTERMS.isPartOf, PKG)); mod_res.add((miri, DCTERMS.identifier, Literal(mid)))
    mod_res.add((miri, RDFS.label, Literal(mlabel, lang="en"))); mod_res.add((miri, OWL.versionInfo, Literal("5.1.0")))
    mod_res.add((miri, RDFS.comment, Literal(f"Module of the AI4SE package; {member_count[mid]} named terms were defined in this module's source." if mid!="ReferencedButUndefined" else f"Module of the AI4SE package; holds {member_count[mid]} stubs.", lang="en")))
modiri = {m[1]: m[2] for m in MODULES}; modiri["ReferencedButUndefined"] = STUB_MOD[1]
for s, mods in defined_in.items():
    if s in {m[2] for m in MODULES}: continue
    if any((s, None, None) in merged for _ in [0]) or (None, None, s) in merged:
        for m in mods: merged.add((s, DCTERMS.isPartOf, modiri[m]))

# ---- role split ---------------------------------------------------------------------------
T_TYPES = {OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty, OWL.SymmetricProperty,
           OWL.TransitiveProperty, OWL.FunctionalProperty, OWL.InverseFunctionalProperty, OWL.Restriction, RDF.Property, OWL.Ontology}
def closure(g, s, out, seen):
    for p, o in g.predicate_objects(s):
        out.add((s, p, o))
        if isinstance(o, BNode) and o not in seen:
            seen.add(o); closure(g, o, out, seen)
tg, ag, shg = Graph(), Graph(), Graph()
named = {s for s in merged.subjects() if isinstance(s, URIRef)}
orphan_b = 0
for s in sorted(named, key=str):
    types = set(merged.objects(s, RDF.type))
    is_s = bool(types & {SH.NodeShape, SH.PropertyShape})
    is_t = bool(types & T_TYPES) or not types
    trip = set(); closure(merged, s, trip, {s})
    for t in trip: (shg if is_s else tg if is_t else ag).add(t)
# any bnode subject not reached from a named subject: keep with the T-Box (axioms)
reached = {t[0] for t in tg} | {t[0] for t in ag} | {t[0] for t in shg}
for s in set(merged.subjects()):
    if isinstance(s, BNode) and s not in reached:
        trip = set(); closure(merged, s, trip, {s}); orphan_b += 1
        for t in trip: tg.add(t)
# modules into the T-Box
for t in mod_res: tg.add(t)

# every individual's class must be reachable: individual types stay as written
# ---- headers ------------------------------------------------------------------------------
def header(g, iri, title, comment, imports=()):
    g.add((iri, RDF.type, OWL.Ontology)); g.add((iri, OWL.versionInfo, Literal("5.1.0" if iri != PKG_S else "1.1.0")))
    ver = "5.1.0" if iri != PKG_S else "1.1.0"
    g.add((iri, OWL.versionIRI, URIRef(str(iri) + "/" + ver)))
    g.add((iri, RDFS.label, Literal(title, lang="en"))); g.add((iri, RDFS.comment, Literal(comment, lang="en")))
    g.add((iri, DCTERMS.contributor, Literal("Yusuf Altunel (curator)")))
    g.add((iri, DCTERMS.provenance, Literal("An AI product: developed with various Claude models (Anthropic) under the curation of Yusuf Altunel.", lang="en")))
    g.add((iri, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by/4.0/")))
    for i in imports: g.add((iri, OWL.imports, i))
tg.add((PKG, OWL.priorVersion, URIRef("http://ai4se.org/ontology/v4")))
header(tg, PKG, "AI4SE ontology, edition 5.1: terminology",
       "Every class and property of the AI4SE ontology: the 4.5 Enterprise concept hierarchy, the 5.0 enrichment modules, the version 1.0 modules and the Enhanced Complete specification, consolidated into one T-Box. Each former source file is a module (dcterms:isPartOf).")
header(ag, PKG_A, "AI4SE ontology, edition 5.1: individuals",
       "Every named individual of the AI4SE ontology (tools, scenario instances, competency questions, requirements, test cases and term definitions).", (PKG,))
bind(tg); bind(ag)

# ---- SHACL --------------------------------------------------------------------------------
sg = bind(Graph())
header(sg, PKG_S, "AI4SE ontology, edition 5.1: shapes",
       "Constraints for the AI4SE package: every class, property and individual carries a human label; every module is complete; a definition is requested for classes (advisory).", (PKG,))
S = Namespace("http://ai4se.org/ontology/v5/shape/")
def shape(name, **kw):
    n = S[name]; sg.add((n, RDF.type, SH.NodeShape)); return n
def prop(n, path, **kw):
    b = BNode(); sg.add((n, SH.property, b)); sg.add((b, SH.path, path))
    for k, v in kw.items(): sg.add((b, getattr(SH, k), v if isinstance(v, (URIRef, Literal)) else Literal(v)))
    return b
def classshape(nm, path, msg, severity=None, **kw):
    """A shape for named (IRI) classes only: anonymous class expressions (blank nodes) are exempt."""
    n = shape(nm); sg.add((n, SH.targetClass, OWL.Class)); sg.add((n, SH.message, Literal(msg, lang="en")))
    if severity is not None: sg.add((n, SH.severity, severity))
    anon, named = BNode(), BNode(); sg.add((anon, SH.nodeKind, SH.BlankNode)); sg.add((named, RDF.type, SH.NodeShape))
    b = BNode(); sg.add((named, SH.property, b)); sg.add((b, SH.path, path)); sg.add((b, SH.minCount, Literal(1)))
    for k, v in kw.items(): sg.add((b, getattr(SH, k), v))
    lst = BNode(); sg.add((n, SH["or"], lst)); sg.add((lst, RDF.first, anon)); r = BNode(); sg.add((lst, RDF.rest, r)); sg.add((r, RDF.first, named)); sg.add((r, RDF.rest, RDF.nil))
for nm, tgt, msg in [("IndividualLabelShape", OWL.NamedIndividual, "Every named individual needs a human-readable label (B7)."),
                     ("ObjectPropertyLabelShape", OWL.ObjectProperty, "Every object property needs a human-readable label (B7)."),
                     ("DatatypePropertyLabelShape", OWL.DatatypeProperty, "Every datatype property needs a human-readable label (B7).")]:
    n = shape(nm); sg.add((n, SH.targetClass, tgt)); prop(n, RDFS.label, minCount=Literal(1), message=Literal(msg, lang="en"))
classshape("ClassLabelShape", RDFS.label, "Every named class needs a human-readable label (B7).")
classshape("ClassDefinitionShape", SKOS.definition, "Advisory: a class should carry a skos:definition. A Warning is not conformance (L-66).", severity=SH.Warning)
n = shape("ModuleShape"); sg.add((n, SH.targetSubjectsOf, DCTERMS.identifier))
prop(n, DCTERMS.isPartOf, minCount=Literal(1), hasValue=PKG, message=Literal("Every module is part of the package ontology.", lang="en"))
prop(n, RDFS.label, minCount=Literal(1), message=Literal("Every module needs a human-readable label.", lang="en"))
prop(n, OWL.versionInfo, minCount=Literal(1), message=Literal("Every module needs its own version.", lang="en"))
classshape("MembershipShape", DCTERMS.isPartOf, "Every named class belongs to at least one module (M1).", nodeKind=SH.IRI)

for t in shg: sg.add(t)
for n_ in set(shg.subjects(RDF.type, SH.NodeShape)) | set(shg.subjects(SH.path, None)):
    if (n_, SH.severity, None) not in sg: sg.add((n_, SH.severity, SH.Warning))   # source constraints are reported, not gated (see findings register)
# ---- write --------------------------------------------------------------------------------
os.makedirs(os.path.join(OUT, "01-ontologies"), exist_ok=True); os.makedirs(os.path.join(OUT, "02-shacl"), exist_ok=True)
os.makedirs(os.path.join(OUT, "04-documentation"), exist_ok=True)
def write(g, path):
    if any(isinstance(x, BNode) for t in g for x in t):
        cg = Graph()
        for t in to_canonical_graph(g): cg.add(t)      # deterministic blank-node labels
        bind(cg)
    else:
        cg = g
    for pre, ns in g.namespaces(): cg.bind(pre, ns, override=True)
    cg.serialize(destination=path, format="turtle")
write(tg, os.path.join(OUT, "01-ontologies", "ai4se_tbox_v5_1_0.ttl"))
write(ag, os.path.join(OUT, "01-ontologies", "ai4se_abox_v5_1_0.ttl"))
write(sg, os.path.join(OUT, "02-shacl", "ai4se_shacl_v1_1_0.ttl"))

def esc(x): return x.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "")
with open(os.path.join(OUT, "04-documentation", "QUARANTINED_CLAIMS_v1_0_1.tsv"), "w", encoding="utf-8") as f:
    f.write("rule\tmodule\tsubject label\tsubject IRI\tproperty\tvalue\n")
    for mid, sl, si, p, o, rule in sorted(quarantine, key=lambda r: (r[5], r[0], r[2], r[3], r[4])):
        f.write("\t".join(esc(x) for x in (rule, mid, sl, si, p, o)) + "\n")

cnt = collections.Counter(r[5] for r in quarantine)
rep = {"modules": len(MODULES), "t_triples": len(tg), "a_triples": len(ag), "s_triples": len(sg),
       "classes": len(set(tg.subjects(RDF.type, OWL.Class))), "individuals": len(set(ag.subjects(RDF.type, OWL.NamedIndividual))),
       "object_properties": len(set(tg.subjects(RDF.type, OWL.ObjectProperty))),
       "datatype_properties": len(set(tg.subjects(RDF.type, OWL.DatatypeProperty))),
       "quarantined": dict(cnt), "quarantined_total": len(quarantine), "q1_pairs": len(Q1_PAIRS),
       "bridges": len(bridges), "stub_classes": len(stub_classes), "stub_tools": len(stub_tools), "stub_properties": len(stub_props),
       "bridge_names": bridges, "closematch_internal": align_internal, "closematch_o4se": align_o4se, "closematch_o4se_ambiguous": o4se_ambiguous, "closematch_o4se_stubs": align_o4se_stub, "derived_labels": len(derived_labels), "derived_label_ids": derived_labels, "extracted_shapes": len(set(shg.subjects(RDF.type, SH.NodeShape)))}
json.dump(rep, open(os.path.join(OUT, "04-documentation", "BUILD_REPORT_v1_1_0.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in rep.items() if k != "bridge_names"}, indent=1))
