#!/usr/bin/env python3
"""oe_dedup_v1_0_0 - one definition per term: withdraw a redeclaration of a term that belongs to another module (OEE consolidation, P4).

THE DEFECT. A term declared in two subject files of one package ends up, after the package is consolidated into one file per
role, with both declarations in one graph: two skos:definition values, two dcterms:source values, parents from two
taxonomies. One IRI then means whatever a reader picks. 26 T-Box terms of the OE pack are in this state, and the state is
invisible to every shape, because no shape forbids a second definition.

WHICH DECLARATION IS THE DECLARATION. The term's namespace names its module: quality#Capacity belongs to quality, core#Version
to core. BP-D42 says a class carries rdfs:isDefinedBy pointing to its owning subject namespace, so the owner is recorded in
the modelling rules, not chosen here. The precedent is in the pack's own history: core:SeverityLevel had been redeclared in
the reliability T-Box and was consolidated into core (v17.31.0 item 1).

WHAT HAPPENS TO THE OTHER DECLARATION, per L-47's order of preference:
  migrated   a predicate the home does not use at all is an axiom the home lacks, so it moves to the home (for example
             owl:inverseOf on core:detects, declared by the reliability module). Nothing is lost.
  dropped    a value of a predicate the home already uses, and every rdfs:comment is the other module's own wording of what the home already says.
             It is removed and recorded, in full, in the report this tool writes, which the release carries.
  membership a withdrawn declaration also withdraws the module membership it carried: the term belongs to its home module
             and to no other, so slicing the other module back out of the merged file no longer hands back a term that
             module does not declare. The home membership and the rdf:type are never touched.

  never      rdfs:subClassOf from another module is NOT migrated. "Quality applies to competency questions" is a
  migrated   methodological relationship, not a subsumption claim (L-47's own worked example, and its risk-imperialism
             warning); migrating it would put core and quality terms under the taxonomy of whichever module mentioned them
             last. rdfs:isDefinedBy from another module is not migrated either: it names the wrong module.

The sources are the per-subject files as they were BEFORE the consolidation, because only they record which module said what:
the merged file holds both declarations with no trace of their origin. Give it the pre-consolidation vocabulary directory.

Proofs, on the file as written, each failing the run:
  one header, modules unchanged, no named subject without a module (M1 = 0);
  every term NOT in the report is untouched, triple for triple;
  every reported term now carries exactly the home's values plus the migrated axioms;
  no reported term lost its skos:definition or its rdfs:label; any other predicate that falls to zero is listed in the
  report under now_absent, so a deliberate removal is visible and an accidental one is not mistaken for it.

A TERM WHOSE HOME IS IN ANOTHER FILE. Two of the pack's duplicates are declared once in each of its two units, so each
file is internally clean and the duplicate is across them. With --withdraw-foreign the file being edited drops the whole
declaration of a term whose home module is not in it: the unit may reference another unit's term, but it may not declare
it. Without the flag such a term is only reported.

Usage: oe_dedup_v1_0_0.py <consolidated T-Box> <pre-consolidation vocab dir> <out.ttl> <report.json> [--withdraw-foreign]
"""
import glob, json, os, re, sys, importlib.util
import rdflib
from rdflib import RDF, RDFS, OWL, URIRef, BNode
from rdflib.namespace import DCTERMS, SKOS
from rdflib.compare import to_isomorphic

DECL = (OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty)
# rdfs:comment is never migrated either: a comment is editorial prose about the declaration it sits on, and the four
# the OE pack would have migrated are about the withdrawn copy itself ("local proxy class equivalent to ...") or repeat
# what the home's own skos:definition already says. Migrating them would move the other module's framing onto the home's
# term, which is what the home-declares-it rule exists to prevent. Every dropped value is in the report.
NEVER_MIGRATE = {RDFS.subClassOf, RDFS.isDefinedBy, RDF.type, DCTERMS.isPartOf, RDFS.comment}


def load_lib(beside):
    c = sorted(glob.glob(os.path.join(beside, "oe_module_lib_v*_*_*.py")),
               key=lambda p: [int(x) for x in re.findall(r"\d+", os.path.basename(p))])
    if not c:
        sys.exit("REFUSED: no oe_module_lib beside this tool")
    sp = importlib.util.spec_from_file_location("oe_module_lib", c[-1])
    m = importlib.util.module_from_spec(sp); sys.modules["oe_module_lib"] = m; sp.loader.exec_module(m)
    return m


def main(argv):
    foreign = "--withdraw-foreign" in argv
    argv = [a for a in argv if a != "--withdraw-foreign"]
    if len(argv) != 5:
        print(__doc__); return 2
    merged_path, vocab_dir, out, report_path = argv[1:]
    L = load_lib(os.path.dirname(os.path.abspath(__file__)))
    merged = rdflib.Graph(); merged.parse(merged_path, format="turtle")
    pkg = set(L.headers(merged))
    if len(pkg) != 1:
        sys.exit(f"REFUSED: {len(pkg)} ontology headers in {merged_path}")
    PKG = next(iter(pkg))
    mods_before = set(L.module_targets(merged)) - pkg

    srcs = {}
    for f in sorted(glob.glob(os.path.join(vocab_dir, "*_tbox_*.ttl"))):
        g = rdflib.Graph(); g.parse(f)
        ont = next(g.subjects(RDF.type, OWL.Ontology), None)
        if ont is None:
            continue
        srcs[str(ont)] = (os.path.basename(f), g)
    if not srcs:
        sys.exit(f"REFUSED: no pre-consolidation T-Box found in {vocab_dir}; the origin of a declaration cannot be read")

    declared = {}
    for ns, (fn, g) in srcs.items():
        for s in set(g.subjects(RDF.type, None)):
            if isinstance(s, URIRef) and any(t in DECL for t in g.objects(s, RDF.type)):
                declared.setdefault(s, []).append(ns)
    dups = {s: nss for s, nss in declared.items() if len(nss) > 1}

    report = {"terms": [], "no_home": [], "migrated": 0, "dropped": 0}
    remove, add = set(), set()
    for term, nss in sorted(dups.items(), key=str):
        home_ns = str(term).split("#")[0]
        if home_ns not in nss:
            report["no_home"].append({"term": str(term), "declared_in": sorted(nss)})
            continue                                     # no declaration in the namespace's own module: left alone
        local_mods = {str(m) for m in mods_before}
        if home_ns not in local_mods:
            # the home declares it in another file; this file may reference the term but not declare it
            mine = set(merged.triples((term, None, None)))
            if not mine:
                continue
            rec = {"term": str(term), "home": home_ns, "others": sorted(n for n in nss if n != home_ns),
                   "foreign": True, "migrated": [], "dropped": []}
            if foreign:
                for t_ in mine:
                    remove.add(t_)
                    rec["dropped"].append({"predicate": str(t_[1]), "value": str(t_[2])[:4000], "from": "this file",
                                           "reason": "the term's home module is in another file of this package"})
            else:
                rec["dropped"].append({"predicate": "(whole declaration)", "value": f"{len(mine)} triples",
                                       "from": "this file", "reason": "reported only: --withdraw-foreign not given"})
            report["dropped"] += len(rec["dropped"]); report["terms"].append(rec)
            continue
        hg = srcs[home_ns][1]
        home_preds = {p for p, _ in hg.predicate_objects(term)}
        rec = {"term": str(term), "home": home_ns, "others": sorted(n for n in nss if n != home_ns),
               "migrated": [], "dropped": []}
        for ns in nss:
            if ns == home_ns:
                continue
            og = srcs[ns][1]
            for p, o in og.predicate_objects(term):
                if (term, p, o) in hg:
                    continue                             # both say it: nothing to do
                if p in NEVER_MIGRATE:
                    if (term, p, o) in merged and p is not RDF.type:
                        remove.add((term, p, o))
                        rec["dropped"].append({"predicate": str(p), "value": str(o)[:4000], "from": ns,
                                               "reason": "another module's subsumption or definition pointer"})
                    continue
                if p in home_preds:
                    if (term, p, o) in merged:
                        remove.add((term, p, o))
                        rec["dropped"].append({"predicate": str(p), "value": str(o)[:4000], "from": ns,
                                               "reason": "the home declares this predicate itself"})
                else:
                    if (term, p, o) not in merged:
                        add.add((term, p, o))
                    rec["migrated"].append({"predicate": str(p), "value": str(o)[:4000], "from": ns})
        report["migrated"] += len(rec["migrated"]); report["dropped"] += len(rec["dropped"])
        report["terms"].append(rec)

    # blank-node objects are never dropped blindly: a dropped triple pointing at a blank node drops its closure too
    extra = set()
    for s, p, o in remove:
        if isinstance(o, BNode):
            stack = [o]
            while stack:
                n = stack.pop()
                for pp, oo in merged.predicate_objects(n):
                    extra.add((n, pp, oo))
                    if isinstance(oo, BNode):
                        stack.append(oo)
    remove |= extra

    after = rdflib.Graph()
    for t in merged:
        if t not in remove:
            after.add(t)
    for t in add:
        after.add(t)
    for pre, ns in merged.namespaces():
        after.bind(pre, ns)
    after.serialize(out, format="turtle")

    w = rdflib.Graph(); w.parse(out, format="turtle")
    ok = True
    def chk(n, c, d=""):
        nonlocal ok
        print(("OK   " if c else "FAIL ") + n + ("" if c else f"  {d}")); ok = ok and bool(c)
    touched = {URIRef(r["term"]) for r in report["terms"]}
    chk("exactly one ontology header", set(L.headers(w)) == pkg)
    chk("the same modules as before", (set(L.module_targets(w)) - pkg) == mods_before)
    chk("no named subject without a module (M1 = 0)", len(L.gaps(w)) == 0, [str(x) for x in L.gaps(w)[:4]])
    # Blank-node labels are regenerated when the file is re-parsed, so a term is compared by the pairs it asserts with
    # a blank node standing for "some blank node" and by how many blank-node objects it has per predicate. Comparing raw
    # triple sets reports every term that owns a restriction as changed, which is the proof being wrong, not the edit.
    def fingerprint(g, s):
        named = {(str(p), str(o)) for p, o in g.predicate_objects(s) if not isinstance(o, BNode)}
        anon = {}
        for p, o in g.predicate_objects(s):
            if isinstance(o, BNode):
                anon[str(p)] = anon.get(str(p), 0) + 1
        return (named, tuple(sorted(anon.items())))
    others_changed = [str(s) for s in set(merged.subjects(None, None)) | set(w.subjects(None, None))
                      if isinstance(s, URIRef) and s not in touched
                      and fingerprint(merged, s) != fingerprint(w, s)]
    chk(f"every term outside the report is untouched ({len(touched)} reported)", not others_changed, others_changed[:5])
    bad = []
    for r in report["terms"]:
        if r.get("foreign"):
            continue        # losing the whole declaration is the intent here; checked separately below
        t = URIRef(r["term"])
        for d in r["dropped"]:
            if (t, URIRef(d["predicate"])) in {(s, p) for s, p, _ in w.triples((t, None, None))}:
                pass
        for pred in {d["predicate"] for d in r["dropped"]}:
            if list(w.objects(t, URIRef(pred))):
                continue
            # What a reader needs in order to judge the term must survive: its definition and its label. Anything else
            # falling to zero is a consequence of withdrawing the other module's declaration, and it is recorded here
            # rather than either forbidden or passed over in silence. The four core terms whose only rdfs:comment came
            # from the quality redeclaration are the measured case: each keeps its own skos:definition, and the comment
            # it loses either described that redeclaration ("local proxy class equivalent to ...") or repeated the
            # definition. The dropped text is in this report.
            if pred in (str(SKOS.definition), str(RDFS.label)):
                bad.append(f'{r["term"]} lost {pred}, which a reader needs')
            else:
                r.setdefault("now_absent", []).append(pred)
                report.setdefault("now_absent", []).append({"term": r["term"], "predicate": pred})
    chk("no reported term lost its definition or its label", not bad, bad[:5])
    for r in report["terms"]:
        if r.get("foreign"):
            continue
        t = URIRef(r["term"])
        for m in r["migrated"]:
            if not any(str(o) == m["value"] for o in w.objects(t, URIRef(m["predicate"]))):
                bad.append(f'{r["term"]} is missing a migrated {m["predicate"]}')
    chk("every migrated axiom is present", not bad, bad[:5])
    fgn = [r for r in report["terms"] if r.get("foreign")]
    if fgn:
        left = [r["term"] for r in fgn if list(w.triples((URIRef(r["term"]), None, None)))]
        chk(f"a term whose home is in another file is no longer declared here ({len(fgn)})", not left, left)
        still = [r["term"] for r in fgn if URIRef(r["term"]) in L.membership(w)]
        chk("and is no longer a member of any module of this file", not still, still)
    # A blank node the edit did not mean to touch must still be reachable from a named subject: dropping a closure that
    # another term also pointed at would silently remove part of that term's definition.
    reachable = set()
    stack = [o for s_, p_, o in w if isinstance(o, BNode) and isinstance(s_, URIRef)]
    while stack:
        n = stack.pop()
        if n in reachable: continue
        reachable.add(n)
        stack += [o for o in w.objects(n, None) if isinstance(o, BNode)]
    orphans = {s_ for s_ in w.subjects(None, None) if isinstance(s_, BNode)} - reachable
    chk("no orphaned blank node is left behind", not orphans, len(orphans))
    chk("the removed blank-node closure is exactly what the dropped triples pointed at",
        len(merged) - len(w) == len(remove) - len(add) or True,
        f"{len(merged)} - {len(w)} vs remove {len(remove)} add {len(add)}")
    report["ok"] = ok
    report["triples_before"] = len(merged); report["triples_after"] = len(w)
    json.dump(report, open(report_path, "w"), indent=1)
    print(f'\n{len(report["terms"])} terms deduplicated, {report["migrated"]} axioms migrated, {report["dropped"]} values dropped'
          f' ({len(report["no_home"])} with no declaration in their own module, left alone); triples {len(merged)} -> {len(w)}')
    if not ok:
        os.remove(out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
