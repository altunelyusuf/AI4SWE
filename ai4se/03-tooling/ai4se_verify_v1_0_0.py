#!/usr/bin/env python3
"""ai4se_verify_v1_0_0.py -- measure the AI4SE package. Usage: python3 -I ai4se_verify_v1_0_0.py <package-dir>
Prints one line per check and a final VERDICT. Exit 0 = PASS, 1 = FAIL.
Checks: the three files parse; each carries exactly one owl:Ontology header; the shapes conform on the T-Box plus A-Box;
the shapes REJECT a known-bad fixture (L-95); no term is used without being typed; the quarantine register is present."""
import sys, os, glob, collections
import rdflib
from rdflib import RDF, OWL, RDFS, URIRef
from rdflib.namespace import DCTERMS, SKOS
root = sys.argv[1]
fails = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (" -- " + detail if detail else ""))
    if not ok: fails.append(name)
def one(pattern):
    m = sorted(glob.glob(os.path.join(root, pattern))); assert len(m) == 1, (pattern, m); return m[0]
tb, ab, sh = one("01-ontologies/ai4se_tbox_v*.ttl"), one("01-ontologies/ai4se_abox_v*.ttl"), one("02-shacl/ai4se_shacl_v*.ttl")
G = {}
for k, f in (("tbox", tb), ("abox", ab), ("shacl", sh)):
    g = rdflib.Graph(); g.parse(f, format="turtle"); G[k] = g
    h = list(g.subjects(RDF.type, OWL.Ontology))
    check(f"{k}: parses ({len(g)} triples) and has exactly one owl:Ontology header", len(h) == 1, f"{len(h)} header(s)")
T, A, S = G["tbox"], G["abox"], G["shacl"]
data = rdflib.Graph()
for g in (T, A): data += g
V = ("http://ai4se.org/ontology/v4#", "http://ai4se.org/ontology/v5#")
typed = set(data.subjects(RDF.type, None))
used = {x for s, p, o in data for x in (s, p, o) if isinstance(x, URIRef) and str(x).startswith(V)}
modules = set(data.subjects(DCTERMS.identifier, None))     # a module is an untyped resource by the discipline (BP-D54)
untyped = sorted(str(x) for x in used - typed - modules)
check("every term in the two namespaces that is used is also typed (no dangling terms)", not untyped, f"{len(untyped)} untyped, e.g. {untyped[:3]}")
check("no individual in the T-Box, no class in the A-Box", not list(T.subjects(RDF.type, OWL.NamedIndividual)) and not list(A.subjects(RDF.type, OWL.Class)))
import pyshacl
from rdflib.namespace import SH
conf, rg, txt = pyshacl.validate(data, shacl_graph=S, inference="none", allow_warnings=True)
sev = collections.Counter(str(o).split("#")[-1] for o in rg.objects(None, SH.resultSeverity))
check("shapes conform on T-Box + A-Box", conf and sev.get("Violation", 0) == 0, f"violations {sev.get('Violation', 0)}; advisory warnings {sev.get('Warning', 0)} (a warning is not conformance, L-66)")
fx = rdflib.Graph(); fx.parse(one("03-tooling/fixtures/negative_class_without_label_v*.ttl"), format="turtle")
c2, _, t2 = pyshacl.validate(fx, shacl_graph=S, inference="none", allow_warnings=True)
check("shapes REJECT the known-bad fixture (the gate can fail, L-95)", (not c2), "fixture rejected" if not c2 else "fixture was accepted")
q = glob.glob(os.path.join(root, "04-documentation/QUARANTINED_CLAIMS_v*.tsv"))
check("quarantine register present", len(q) == 1, f"{sum(1 for _ in open(q[0], encoding='utf-8')) - 1} rows" if q else "missing")
nodef = sum(1 for c in T.subjects(RDF.type, OWL.Class) if isinstance(c, URIRef) and not (c, SKOS.definition, None) in T)
ncls = len(set(T.subjects(RDF.type, OWL.Class)))
print(f"INFO classes: {ncls}; without skos:definition (advisory, not conformance): {nodef}")
print("VERDICT: " + ("PASS" if not fails else "FAIL (" + "; ".join(fails) + ")"))
sys.exit(1 if fails else 0)
