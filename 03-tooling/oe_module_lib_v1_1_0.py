#!/usr/bin/env python3
"""oe_module_lib_v1_1_0 - modules inside the three files of a package (BP-D54): membership, slices, and the proofs that a merge of several
former subject files lost and invented nothing.

Vocabulary. A package ontology (the one owl:Ontology header of a file) has MODULES: untyped resources at the former subjects' IRIs that carry
dcterms:isPartOf <package ontology IRI>. A MEMBER is a named subject that carries dcterms:isPartOf <module IRI>. Before a merge, the old file's own
header IRI stands in as the module (a term of core_tbox is part of the core header); after it, the module resource at that IRI takes over, so a
term's membership triple does not change in the merge. (rdfs:isDefinedBy is NOT used for membership: measured on the OE pack, 443 A-Box
individuals carry an isDefinedBy that names a finer sub-topic, so it cannot say which file a term came from.)

v1.1.0: (1) a subject whose IRI lies below a header IRI is no longer taken for a version IRI (see _version_iris); (2) the invertibility proof drops, with a term that two parts both define, the blank-node clusters only that term pointed to (a slice holds the clusters of BOTH definitions, the part only its own, so a restriction on a duplicated class made the proof fail on a real, correct merge: found on the 26 duplicate T-Box terms of the OE pack).

API (all take rdflib graphs):
  headers(g), module_targets(g), named_subjects(g)       the vocabulary above
  membership(g) -> {subject: {module IRIs}}              from dcterms:isPartOf, restricted to the module targets of g
  gaps(g)       -> sorted named subjects with no membership
  slice(g, module) -> Graph                              all triples of the module's members, with their blank-node closure
  body(g)       -> Graph                                 g without the header, its version IRIs and the module resources (the content)
  merge(parts, package_iri, meta) -> Graph               union of the parts' bodies plus one module resource per part (no header: the caller owns it)
  equal(a, b)   -> (bool, ...)                           graph equality by per-subject cluster signatures with canonical blank-node closures
  prove_union(parts, merged)      -> dict                the merged body equals the union of the parts' bodies (modules aside)
  prove_invertible(parts, merged) -> dict                slicing the merged graph by module reproduces each part, except for terms that two
                                                         parts both define (those are listed and only checked in the union)
Proofs are tested to discriminate: a removed triple, an added triple and a removed blank-node triple each make them fail (see the test)."""
import sys
import rdflib
from rdflib import BNode, Graph, Literal, URIRef, RDF, RDFS, OWL
from rdflib.compare import to_canonical_graph

DCT = "http://purl.org/dc/terms/"
IS_PART_OF = URIRef(DCT + "isPartOf")
IDENT = URIRef(DCT + "identifier")


def headers(g):
    return {s for s in g.subjects(RDF.type, OWL.Ontology) if isinstance(s, URIRef)}


def _module_resources(g):
    # a module resource is untyped and carries dcterms:identifier; a term of a not yet merged file also says isPartOf <header>, but it is typed
    hs = headers(g)
    return {m for m, p in g.subject_objects(IS_PART_OF)
            if p in hs and m not in hs and isinstance(m, URIRef) and (m, RDF.type, None) not in g and (m, IDENT, None) in g}


def module_targets(g):
    return headers(g) | _module_resources(g)


def _version_iris(g):
    """the version IRIs a header declares (owl:versionIRI, owl:priorVersion). v1.0.0 took every IRI below a header's IRI for a version IRI and so dropped real subjects
    (66 quality individuals under .../quality/sparql-impl-v1.0.0# and one shape under .../drift18# on the OE pack) from the merge and from its own proof alike."""
    return {o for h in headers(g) for p in (OWL.versionIRI, OWL.priorVersion) for o in g.objects(h, p)}


def named_subjects(g):
    hs = headers(g); ms = _module_resources(g); vi = _version_iris(g)
    return {s for s in set(g.subjects()) if isinstance(s, URIRef) and s not in hs and s not in ms and s not in vi}


def membership(g):
    tg = module_targets(g)
    out = {}
    for s in named_subjects(g):
        out[s] = {o for o in g.objects(s, IS_PART_OF) if o in tg}
    return out


def gaps(g):
    return sorted(s for s, m in membership(g).items() if not m)


def _closure(g, node, out, seen):
    for p, o in g.predicate_objects(node):
        out.add((node, p, o))
        if isinstance(o, BNode) and o not in seen:
            seen.add(o); _closure(g, o, out, seen)


def slice(g, module):
    out = Graph()
    for s, mods in membership(g).items():
        if module in mods:
            tr = set(); seen = set()
            for p, o in g.predicate_objects(s):
                tr.add((s, p, o))
                if isinstance(o, BNode) and o not in seen:
                    seen.add(o); _closure(g, o, tr, seen)
            for t in tr: out.add(t)
    return out


def body(g):
    hs = headers(g); ms = _module_resources(g); vi = _version_iris(g)
    out = Graph()
    for s, p, o in g:
        if isinstance(s, URIRef) and (s in hs or s in ms or s in vi):
            continue
        out.add((s, p, o))
    return out


def merge(parts, package_iri, meta):
    """parts: {module IRI: Graph of the old file}; meta: {module IRI: {'identifier':..., 'label':..., 'version':...}}"""
    out = Graph()
    for mod, g in parts.items():
        for t in body(g): out.add(t)
        m = URIRef(mod); i = meta[mod]
        out.add((m, IS_PART_OF, URIRef(package_iri)))
        out.add((m, IDENT, Literal(i["identifier"])))
        out.add((m, RDFS.label, Literal(i["label"])))
        out.add((m, OWL.versionInfo, Literal(i["version"])))
    return out


def sig(g):
    named = {}
    for s, p, o in g:
        if isinstance(s, BNode): continue
        named.setdefault(s, []).append((p, o))

    def closure(b, seen):
        tr = []
        for p, o in g.predicate_objects(b):
            tr.append((b, p, o))
            if isinstance(o, BNode) and o not in seen:
                seen.add(o); tr += closure(o, seen)
        return tr
    out = set()
    for s, pos in named.items():
        plain = []; cl = Graph()
        for p, o in pos:
            if isinstance(o, BNode):
                for t in closure(o, {o}): cl.add(t)
                cl.add((s, p, o))
            else:
                plain.append((str(s), str(p), o.n3()))
        h = None
        if len(cl):
            cg = to_canonical_graph(cl)
            h = tuple(sorted((x.n3(), y.n3(), z.n3()) for x, y, z in cg))
        out.add((str(s), tuple(sorted(plain)), h))
    return out, sum(1 for s, p, o in g if isinstance(s, BNode))


def equal(a, b):
    sa, na = sig(a); sb, nb = sig(b)
    return sa == sb and na == nb, len(sa), len(sb), na, nb


def _resource_triples(g):
    ms = _module_resources(g)
    out = Graph()
    for s, p, o in g:
        if s in ms: out.add((s, p, o))
    return out


def _without(g, subjects):
    """g without the triples of `subjects`, and without the blank-node clusters that only they pointed to (an orphaned cluster is part of the dropped term)"""
    out = Graph()
    for s, p, o in g:
        if not (isinstance(s, URIRef) and s in subjects): out.add((s, p, o))
    reach = set(); stack = [o for s, p, o in out if isinstance(s, URIRef) and isinstance(o, BNode)]
    while stack:
        b = stack.pop()
        if b in reach: continue
        reach.add(b)
        stack += [o for o in out.objects(b, None) if isinstance(o, BNode)]
    drop = [(s, p, o) for s, p, o in out if isinstance(s, BNode) and s not in reach]
    for t in drop: out.remove(t)
    return out


def prove_union(parts, merged):
    u = Graph()
    for g in parts.values():
        for t in body(g): u.add(t)
    ms = _module_resources(merged)
    content = Graph()
    for t in body(merged):
        if not (isinstance(t[0], URIRef) and t[0] in ms): content.add(t)
    ok, na, nb, bna, bnb = equal(u, content)
    return {"ok": ok, "subjects_parts": na, "subjects_merged": nb, "bnode_triples_parts": bna, "bnode_triples_merged": bnb}


def prove_invertible(parts, merged):
    owners = {}
    for mod, g in parts.items():
        for s in named_subjects(g): owners.setdefault(s, set()).add(mod)
    dups = {s for s, o in owners.items() if len(o) > 1}
    res = {"duplicates": sorted(str(s) for s in dups), "modules": {}, "ok": True}
    for mod, g in parts.items():
        a = _without(slice(merged, URIRef(mod)), dups)
        b = _without(body(g), dups)
        ok = equal(a, b)[0]
        res["modules"][mod] = ok
        res["ok"] = res["ok"] and ok
    return res


def main(argv):
    if len(argv) >= 3 and argv[1] == "gaps":
        bad = 0
        for f in argv[2:]:
            g = Graph(); g.parse(f)
            gp = gaps(g); bad += len(gp)
            print(f"{f}: {len(gp)} named subject(s) without membership of {len(named_subjects(g))}")
            for s in gp[:5]: print("   ", s)
        return 1 if bad else 0
    if len(argv) == 4 and argv[1] == "slice":
        g = Graph(); g.parse(argv[2]); s = slice(g, URIRef(argv[3]))
        print(s.serialize(format="turtle")); return 0
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
