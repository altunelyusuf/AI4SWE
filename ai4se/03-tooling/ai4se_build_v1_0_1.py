#!/usr/bin/env python3
"""ai4se_build_v1_0_1.py -- consolidate the repaired AI4SE source files into the three canonical files.

Input : a folder with the repaired source Turtle files (one per former subject = module).
Output: <out>/01-ontologies/ai4se_tbox_v5_0_1.ttl, ai4se_abox_v5_0_1.ttl, <out>/02-shacl/ai4se_shacl_v1_0_1.ttl
        <out>/04-documentation/QUARANTINED_CLAIMS_v1_0_0.tsv, BUILD_REPORT_v1_0_1.json

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

SRC, OUT = sys.argv[1], sys.argv[2]
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
            "hasTestSuite", "mergeDate", "mergeStrategy", "sourceOntology", "moduleVersion"}
FIG = re.compile(r"\d+(\.\d+)?\s?%|[\$€₺£]\s?\d")
HEADER_PREDS = {DCTERMS.title, DCTERMS.description, DCTERMS.creator, DCTERMS.created, OWL.versionInfo, OWL.priorVersion,
                OWL.versionIRI, OWL.imports, RDFS.comment, RDFS.label, DCTERMS.license, DCTERMS.publisher,
                DCTERMS.modified, DCTERMS.contributor, DCTERMS.identifier, DCTERMS.isPartOf}
KEEP_FIG_PROPS = {"definition", "comment", "label", "prefLabel", "altLabel", "hasFormula", "scopeNote", "hasToolURL"}

# ---- load -------------------------------------------------------------------------------------
graphs = {}
for fn, mid, miri, mlabel in MODULES:
    g = Graph(); g.parse(os.path.join(SRC, fn), format="turtle"); graphs[mid] = g

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
def inpkg(x): return isinstance(x, URIRef) and (str(x).startswith(V4) or str(x).startswith(V5))
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

# ---- module resources ---------------------------------------------------------------------
mod_res = Graph()
member_count = collections.Counter()
for s, mods in defined_in.items():
    for m in mods: member_count[m] += 1
for fn, mid, miri, mlabel in MODULES + [(None,)+STUB_MOD]:
    mod_res.add((miri, DCTERMS.isPartOf, PKG)); mod_res.add((miri, DCTERMS.identifier, Literal(mid)))
    mod_res.add((miri, RDFS.label, Literal(mlabel, lang="en"))); mod_res.add((miri, OWL.versionInfo, Literal("5.0.1")))
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
tg, ag = Graph(), Graph()
named = {s for s in merged.subjects() if isinstance(s, URIRef)}
orphan_b = 0
for s in sorted(named, key=str):
    types = set(merged.objects(s, RDF.type))
    is_t = bool(types & T_TYPES) or not types
    trip = set(); closure(merged, s, trip, {s})
    for t in trip: (tg if is_t else ag).add(t)
# any bnode subject not reached from a named subject: keep with the T-Box (axioms)
reached = {t[0] for t in tg} | {t[0] for t in ag}
for s in set(merged.subjects()):
    if isinstance(s, BNode) and s not in reached:
        trip = set(); closure(merged, s, trip, {s}); orphan_b += 1
        for t in trip: tg.add(t)
# modules into the T-Box
for t in mod_res: tg.add(t)

# every individual's class must be reachable: individual types stay as written
# ---- headers ------------------------------------------------------------------------------
def header(g, iri, title, comment, imports=()):
    g.add((iri, RDF.type, OWL.Ontology)); g.add((iri, OWL.versionInfo, Literal("5.0.1" if iri != PKG_S else "1.0.1")))
    ver = "5.0.1" if iri != PKG_S else "1.0.1"
    g.add((iri, OWL.versionIRI, URIRef(str(iri) + "/" + ver)))
    g.add((iri, RDFS.label, Literal(title, lang="en"))); g.add((iri, RDFS.comment, Literal(comment, lang="en")))
    g.add((iri, DCTERMS.contributor, Literal("Yusuf Altunel (curator)")))
    g.add((iri, DCTERMS.provenance, Literal("An AI product: developed with various Claude models (Anthropic) under the curation of Yusuf Altunel.", lang="en")))
    g.add((iri, DCTERMS.license, URIRef("https://creativecommons.org/licenses/by/4.0/")))
    for i in imports: g.add((iri, OWL.imports, i))
tg.add((PKG, OWL.priorVersion, URIRef("http://ai4se.org/ontology/v4")))
header(tg, PKG, "AI4SE ontology, edition 5.0: terminology",
       "Every class and property of the AI4SE ontology: the 4.5 Enterprise concept hierarchy plus the 5.0 enrichment modules, consolidated into one T-Box. Each former source file is a module (dcterms:isPartOf).")
header(ag, PKG_A, "AI4SE ontology, edition 5.0: individuals",
       "Every named individual of the AI4SE ontology (tools and scenario instances).", (PKG,))
bind(tg); bind(ag)

# ---- SHACL --------------------------------------------------------------------------------
sg = bind(Graph())
header(sg, PKG_S, "AI4SE ontology, edition 5.0: shapes",
       "Constraints for the AI4SE package: every class, property and individual carries a human label; every module is complete; a definition is requested for classes (advisory).", (PKG,))
S = Namespace("http://ai4se.org/ontology/v5/shape/")
def shape(name, **kw):
    n = S[name]; sg.add((n, RDF.type, SH.NodeShape)); return n
def prop(n, path, **kw):
    b = BNode(); sg.add((n, SH.property, b)); sg.add((b, SH.path, path))
    for k, v in kw.items(): sg.add((b, getattr(SH, k), v if isinstance(v, (URIRef, Literal)) else Literal(v)))
    return b
for nm, tgt, msg in [("ClassLabelShape", OWL.Class, "Every class needs a human-readable label (B7)."),
                     ("IndividualLabelShape", OWL.NamedIndividual, "Every named individual needs a human-readable label (B7)."),
                     ("ObjectPropertyLabelShape", OWL.ObjectProperty, "Every object property needs a human-readable label (B7)."),
                     ("DatatypePropertyLabelShape", OWL.DatatypeProperty, "Every datatype property needs a human-readable label (B7).")]:
    n = shape(nm); sg.add((n, SH.targetClass, tgt)); prop(n, RDFS.label, minCount=Literal(1), message=Literal(msg, lang="en"))
n = shape("ClassDefinitionShape"); sg.add((n, SH.targetClass, OWL.Class))
prop(n, SKOS.definition, minCount=Literal(1), severity=SH.Warning,
     message=Literal("Advisory: a class should carry a skos:definition. A Warning is not conformance (L-66).", lang="en"))
n = shape("ModuleShape"); sg.add((n, SH.targetSubjectsOf, DCTERMS.identifier))
prop(n, DCTERMS.isPartOf, minCount=Literal(1), hasValue=PKG, message=Literal("Every module is part of the package ontology.", lang="en"))
prop(n, RDFS.label, minCount=Literal(1), message=Literal("Every module needs a human-readable label.", lang="en"))
prop(n, OWL.versionInfo, minCount=Literal(1), message=Literal("Every module needs its own version.", lang="en"))
n = shape("MembershipShape"); sg.add((n, SH.targetClass, OWL.Class))
prop(n, DCTERMS.isPartOf, minCount=Literal(1), nodeKind=SH.IRI, message=Literal("Every class belongs to at least one module (M1).", lang="en"))

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
write(tg, os.path.join(OUT, "01-ontologies", "ai4se_tbox_v5_0_1.ttl"))
write(ag, os.path.join(OUT, "01-ontologies", "ai4se_abox_v5_0_1.ttl"))
write(sg, os.path.join(OUT, "02-shacl", "ai4se_shacl_v1_0_1.ttl"))

def esc(x): return x.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n").replace("\r", "")
with open(os.path.join(OUT, "04-documentation", "QUARANTINED_CLAIMS_v1_0_0.tsv"), "w", encoding="utf-8") as f:
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
       "bridge_names": bridges}
json.dump(rep, open(os.path.join(OUT, "04-documentation", "BUILD_REPORT_v1_0_1.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in rep.items() if k != "bridge_names"}, indent=1))
