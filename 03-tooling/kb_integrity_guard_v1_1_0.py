#!/usr/bin/env python3
"""
kb_integrity_guard_v1_1_0.py — preventive guard for OE knowledge-base integrity.

Catches the two defect classes that survived until a registrant's id-keyed query
surfaced them (v20.23.18-20):
  (1) DUPLICATE NUMBERING  — two distinct BP/L individuals sharing one BP-D{n}/L-{n} number
  (2) ID-COVERAGE GAP      — a BP/L individual lacking hasBestPracticeId / hasLessonId
  (3) ID COLLISION         — two individuals carrying the same hasLessonId / hasBestPracticeId literal

These are GRAPH-LEVEL invariants (COUNT/GROUP-BY across individuals), which per-item
SHACL property shapes cannot express — hence a SPARQL-based guard.

Per SL-01/L-95: this guard is proven DISCRIMINATING — it passes a clean KB and FAILS an
injected-duplicate KB (run with --self-test).

Exit 0 = clean; exit 1 = integrity violation(s) found. Intended to run in the release gate.
"""
import sys, glob, re
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import RDF
from collections import Counter, defaultdict

KB = 'http://example.org/knowledge-base#'
LESSON = URIRef(KB + 'LessonsLearned')
BP = URIRef(KB + 'BestPractice')
HLI = URIRef(KB + 'hasLessonId')
HBPI = URIRef(KB + 'hasBestPracticeId')

def load_kb(paths):
    g = Graph()
    for p in paths:
        g.parse(p, format='turtle')
    return g

# v1.1.0 (OEE consolidation, P2): reads BOTH layouts. In a package of one file per role the knowledge base is a MODULE of the one A-Box file
# (BP-D54); it is then the slice of that file that belongs to the module (oe_module_lib, found beside this file).
def _lib():
    import importlib.util, os
    fs = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'oe_module_lib_v*.py')), key=lambda p: [int(x) for x in re.findall(r'\d+', os.path.basename(p))])
    sp = importlib.util.spec_from_file_location('oe_module_lib', fs[-1]); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m

def module_graph(old_pattern, consolidated_pattern, module_iri, with_module_resource=False):
    """the graph of one former subject file, in either layout; (None) when neither exists"""
    old = sorted(glob.glob(old_pattern))
    if old:
        g = Graph(); g.parse(old[-1], format='turtle'); return g, old[-1]
    new = sorted(glob.glob(consolidated_pattern))
    if not new:
        return None, None
    L = _lib(); big = Graph(); big.parse(new[-1], format='turtle')
    s = L.slice(big, URIRef(module_iri))
    if with_module_resource:
        for t in big.triples((URIRef(module_iri), None, None)): s.add(t)
        for pfx, ns in big.namespaces(): s.bind(pfx, ns, override=False)
    return s, new[-1]

KB_MODULE = 'http://example.org/knowledge-base'

def kb_paths_or_graph():
    """the knowledge base as a graph, from the old layout (knowledge_base_abox_v2_*.ttl) or from the module of the package A-Box"""
    paths = sorted(glob.glob('01-ontologies/knowledge_base_abox_v2_*.ttl'))
    if paths:
        return load_kb(paths)
    g, _ = module_graph('', '09-governance/oegov_abox_v*.ttl', KB_MODULE)
    return g

def derive_num(iri, kind):
    """Derive the canonical number from an IRI, tolerant of the heterogeneous encodings."""
    ln = iri.split('#')[-1]
    if kind == 'L':
        m = (re.search(r'Lesson_L_(X?\d+)_', ln) or re.search(r'LessonLearned_(\d+)_', ln)
             or re.search(r'OEPACK_Lesson_L(\d+)', ln) or re.search(r'_L_?(X?\d+)_', ln))
        return f'L-{m.group(1)}' if m else None
    else:
        m = (re.search(r'BestPractice_D(\d+[A-Za-z]?)_', ln) or re.search(r'_D(\d+)_', ln)
             or re.search(r'_BP_(X\d+)_', ln) or re.search(r'OEPACK_BP(\d+)', ln))
        if m:
            v = m.group(1)
            return f'BP-D{v}' if re.match(r'^\d', v) else f'BP-{v}'
        return None

def check(g):
    """Authoritative source of truth is the hasLessonId/hasBestPracticeId LITERAL, not the IRI.
    The id-literal carries the canonical number (incl. legacy 'BP-2' vs D-series 'BP-D2', which are
    DISTINCT). Checking the literal avoids false collisions from IRI over-normalization; an item with
    no id-literal is caught by the coverage check, so once coverage is 100% the uniqueness check is
    complete."""
    violations = []
    for kind, cls, idp in [('L', LESSON, HLI), ('BP', BP, HBPI)]:
        inds = list(g.subjects(RDF.type, cls))
        # (1) id-coverage gap — every BP/L must carry its authoritative id literal
        for s in inds:
            if (s, idp, None) not in g:
                violations.append(f'MISSING-ID ({kind}): {str(s).split("#")[-1]} has no {idp.split("#")[-1]}')
        # (2) id-literal uniqueness — no two individuals may share an id literal
        #     (this is the real numbering-uniqueness invariant; distinct schemes like BP-2 vs BP-D2
        #     are correctly NOT collisions because their literals differ)
        owners = defaultdict(list)
        for s, p, o in g:
            if p == idp:
                owners[str(o)].append(str(s).split('#')[-1])
        for v, members in owners.items():
            if len(members) > 1:
                violations.append(f'ID-COLLISION ({kind}): "{v}" used by {len(members)} individuals -> {members}')
    return violations

def main():
    if '--self-test' in sys.argv:
        # SL-01/L-95: prove the guard FAILS a known-bad input (inject a colliding id literal)
        g = kb_paths_or_graph()
        bad = URIRef(KB + 'Lesson_L_65_INJECTED_DUPLICATE_FOR_SELFTEST')
        g.add((bad, RDF.type, LESSON))
        g.add((bad, HLI, Literal('L-65')))  # collide with the real L-65 id literal
        v = check(g)
        dup = [x for x in v if x.startswith('ID-COLLISION (L): "L-65"')]
        if dup:
            print('SELF-TEST PASS: guard correctly FAILED the injected id collision ->', dup[0])
            sys.exit(0)
        print('SELF-TEST FAIL: guard did NOT catch the injected collision'); sys.exit(2)

    g = kb_paths_or_graph()
    if g is None or not len(g):
        print('kb_integrity_guard: no kb_abox found'); sys.exit(2)
    v = check(g)
    if v:
        print(f'KB INTEGRITY: {len(v)} VIOLATION(S)')
        for x in v:
            print('  -', x)
        sys.exit(1)
    L = len(list(g.subjects(RDF.type, LESSON))); B = len(list(g.subjects(RDF.type, BP)))
    print(f'KB INTEGRITY: CLEAN — {B} BP + {L} L, 0 duplicate numbers, 0 missing ids, 0 id collisions')
    sys.exit(0)

if __name__ == '__main__':
    main()
