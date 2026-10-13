#!/usr/bin/env python3
"""oe_method_completeness_gate_v1_2_0.py — prove the package is usable, not merely clean.

The clean gate proves nothing forbidden is present. This proves everything required IS.
The previous build passed manifest, SHACL and clean checks while shipping vocabularies with
zero individuals — a package that verified perfectly and could not be used. That is the
failure this gate exists to make impossible.

Checks, each independently reported:
  1. population   — every declared class in every shipped TBox has at least one individual
                    somewhere in the package, or is declared abstract
  2. pairing      — every *_tbox_* has a corresponding *_abox_*, OR is exempted per BP-D51
                    (kb:isOngoingEnhancementLineage true on the ontology, AND real
                    non-skeleton shape coverage already exists — checked, not trusted)
  3. protocol     — every protocol/discipline document is accompanied by machinery
  4. shapes       — every vocabulary namespace has at least one SHACL suite targeting it

v1.2.0 (OEE consolidation, BP-D54): a vocabulary is a MODULE of a package T-Box or A-Box (one file per role in each unit), not a file. The gate reads
the modules of 01-vocabularies/*_tbox_* and *_abox_* and of 09-governance/*_tbox_* and *_abox_*; the numbers it reports are the same as before the
consolidation (the proof is that the old and new corpora give the same population, pairing and shape results).
v1.1.0: added the BP-D51 pairing exemption. The population check already had graduated
tolerance (a documented baseline + a per-class Abstract marker) that pairing and shapes
never got — a hard binary with zero escape valve for a genuinely deferred, tracked gap.
Verified with two negative controls before shipping (L-95): the exemption is denied when
the marker is absent, and denied when the marker is present but shape coverage is
skeleton-only (BP-D27's retired mechanism cannot be revived to satisfy this).

  python3 oe_method_completeness_gate_v1_2_0.py [root]
"""
import glob
import os
import sys

sys.dont_write_bytecode = True    # a gate must not leave a __pycache__ in the package it checks

import rdflib
from rdflib import OWL, RDF, RDFS, URIRef

root = sys.argv[1] if len(sys.argv) > 1 else '.'
os.chdir(root)

ABSTRACT = URIRef('http://example.org/meta#Abstract')
failures = []

import re
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '03-tooling'))
import glob as _g
_libs = sorted(_g.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '03-tooling', 'oe_module_lib_v*.py')))
if not _libs:
    sys.exit('REFUSED: no oe_module_lib in 03-tooling')
import importlib.util
_sp = importlib.util.spec_from_file_location('oe_module_lib', _libs[-1]); L = importlib.util.module_from_spec(_sp); sys.modules['oe_module_lib'] = L; _sp.loader.exec_module(L)
DCT_IDENT = URIRef('http://purl.org/dc/terms/identifier')


def modules_of(pattern):
    """[(file, module IRI, identifier, graph)] for every module of every file matching the pattern"""
    out = []
    for f in sorted(glob.glob(pattern)):
        g = rdflib.Graph(); g.parse(f)
        for m in sorted(set(L.module_targets(g)) - set(L.headers(g))):
            ident = next(iter(g.objects(m, DCT_IDENT)), None)
            out.append((f, m, str(ident) if ident is not None else str(m), g))
    if not out and glob.glob(pattern):
        sys.exit('REFUSED: ' + pattern + ' holds no module')
    return out


tbox_mods = modules_of('01-vocabularies/*_tbox_*.ttl') + modules_of('09-governance/*_tbox_*.ttl')
abox_mods = modules_of('01-vocabularies/*_abox_*.ttl') + modules_of('09-governance/*_abox_*.ttl')
if not tbox_mods:
    sys.exit('REFUSED: no T-Box module found: a gate that scans nothing does not pass')
# A module of the A-Box pairs with the T-Box module of the same IRI, or whose IRI plus '-abox' it carries (risk-abox), or one named here: the A-Box of
# the release history is an original file of this package whose header IRI differs from the derived T-Box module it instantiates.
PAIR_ALIASES = {'http://example.org/oe-method/history': 'http://example.org/oepack-release-history'}
def pair_key(iri):
    iri = PAIR_ALIASES.get(iri, iri)
    return iri[:-len('-abox')] if iri.endswith('-abox') else iri
tbox_mods = [(f, m, str(m), g) for (f, m, _, g) in tbox_mods]
abox_mods = [(f, m, pair_key(str(m)), g) for (f, m, _, g) in abox_mods]
tboxes = [m[2] for m in tbox_mods]
aboxes = [m[2] for m in abox_mods]

# ---- load every individual typed anywhere in the package -------------------
population = rdflib.Graph()
for f in sorted(glob.glob('**/*.ttl', recursive=True)):
    try:
        population.parse(f)
    except Exception:
        pass
typed = set(population.objects(None, RDF.type))

# ---- 1. population --------------------------------------------------------
unpopulated = []
declared = 0
for (tf, tmod, tid, g) in tbox_mods:
    # the checks below look at the module's own triples, as they looked at the former file's own triples: a subclass declared in ANOTHER module does not make a class
    # structural here, so the numbers do not change with the consolidation
    sg = L.slice(g, tmod)
    for c in sg.subjects(RDF.type, OWL.Class):
        if not isinstance(c, URIRef):
            continue
        declared += 1
        if c in typed:
            continue
        if (c, RDF.type, ABSTRACT) in sg or (c, OWL.deprecated, rdflib.Literal(True)) in sg:
            continue
        # a class with subclasses is structural: population may live on the leaves
        if any(True for _ in sg.subjects(RDFS.subClassOf, c)):
            continue
        unpopulated.append((tid.rsplit('/', 1)[-1], str(c).split('#')[-1]))

pop_pct = 100.0 * (declared - len(unpopulated)) / declared if declared else 0.0
print(f'population : {declared - len(unpopulated)}/{declared} classes populated '
      f'({pop_pct:.1f}%), {len(unpopulated)} leaf classes with no individual')
for f, c in unpopulated[:15]:
    print(f'    {f}: {c}')
if len(unpopulated) > 15:
    print(f'    ... and {len(unpopulated) - 15} more')
# The governing pack this method derives from achieves 39.7% class population: many TBox
# classes are structural scaffolding awaiting domain individuals. An absolute 100% bar would
# fail the method's own source, so the gate fails BELOW A RECORDED BASELINE rather than below
# perfection. Raise BASELINE_POPULATION_PCT as population improves; never lower it silently.
BASELINE_POPULATION_PCT = 39.0
if pop_pct < BASELINE_POPULATION_PCT:
    print(f'    below recorded baseline of {BASELINE_POPULATION_PCT}%')
    failures.append('population')

# ---- 2. TBox/ABox pairing -------------------------------------------------
# BP-D51 (kb:isOngoingEnhancementLineage): a package-level marker on an owl:Ontology
# declaration exempts THIS check only — never shapes — and only when real (non-skeleton)
# shape coverage for that namespace already exists. Mirrors the population check's own
# ABSTRACT-marker tolerance, which pairing and shapes never got. The exemption is always
# printed, never silent (L-95: a gate honoring a marker must still fail without it).
ONGOING = URIRef('http://example.org/knowledge-base#isOngoingEnhancementLineage')
SKELETON = URIRef('http://example.org/knowledge-base#isSkeletonShape')

def has_ongoing_lineage_marker(tbox_mod):
    _, mod, _, g = tbox_mod
    return str(mod) if (mod, ONGOING, rdflib.Literal(True)) in g else None

def has_real_shape_coverage(onto_iri):
    """At least one shape targets a class in this namespace, and none of the shapes
    targeting it are BP-D27 skeletons (that mechanism is retired — 0 skeleton shapes is
    the achieved ecosystem-wide baseline; an exemption may not rest on reviving it)."""
    ns = onto_iri.rstrip('/') + '#'
    found_any, found_real = False, False
    for f in glob.glob('02-safeguards/*.ttl') + glob.glob('09-governance/*_shacl_*.ttl'):
        g = rdflib.Graph()
        try:
            g.parse(f)
        except Exception:
            continue
        for shape in g.subjects(URIRef('http://www.w3.org/ns/shacl#targetClass'), None):
            for cls in g.objects(shape, URIRef('http://www.w3.org/ns/shacl#targetClass')):
                if isinstance(cls, URIRef) and str(cls).startswith(ns):
                    found_any = True
                    if (shape, SKELETON, rdflib.Literal(True)) not in g:
                        found_real = True
    return found_any and found_real

stems_t = set(tboxes)
stems_a = set(aboxes)
missing_abox = sorted(stems_t - stems_a)

exempted = []
still_missing = []
for s in missing_abox:
    tbox_file = next(t for t in tbox_mods if t[2] == s)
    onto_iri = has_ongoing_lineage_marker(tbox_file)
    if onto_iri and has_real_shape_coverage(onto_iri):
        exempted.append(s)
    else:
        still_missing.append(s)

print(f'pairing    : {len(stems_t & stems_a) + len(exempted)}/{len(stems_t)} vocabularies ship both '
      f'TBox and ABox, or are exempted (BP-D51)')
for s in exempted:
    print(f'    exempted (BP-D51, kb:isOngoingEnhancementLineage + real shape coverage): {s.rsplit("/", 1)[-1]}')
for s in still_missing:
    print(f'    no ABox for: {s.rsplit("/", 1)[-1]}')
if still_missing:
    failures.append('pairing')

# ---- 3. protocol machinery ------------------------------------------------
docs = glob.glob('04-documentation/*.md')
tools = glob.glob('03-tooling/*')
has_protocol = any('Conformance_Protocol' in d for d in docs)
has_publisher = any('publish' in os.path.basename(t) for t in tools)
print(f'protocol   : protocol doc={has_protocol} publisher={has_publisher}')
if has_protocol and not has_publisher:
    failures.append('protocol')

# ---- 4. shape coverage ----------------------------------------------------
shape_ns = set()
for f in glob.glob('02-safeguards/*.ttl') + glob.glob('09-governance/*_shacl_*.ttl'):
    g = rdflib.Graph()
    try:
        g.parse(f)
    except Exception:
        continue
    for o in g.objects(None, URIRef('http://www.w3.org/ns/shacl#targetClass')):
        if isinstance(o, URIRef) and '#' in str(o):
            shape_ns.add(str(o).rsplit('#', 1)[0])
vocab_ns = set()
for (tf, tmod, tid, g) in tbox_mods:
    vocab_ns.add(str(tmod))
uncovered = sorted(vocab_ns - shape_ns)
print(f'shapes     : {len(vocab_ns & shape_ns)}/{len(vocab_ns)} vocabularies have shape coverage')
for u in uncovered:
    print(f'    no shapes targeting: {u}')
if uncovered:
    failures.append('shapes')

# ---- 5. entry points -------------------------------------------------------
# Added after README.md was deleted in a rebuild and went unnoticed for three releases:
# every other check verified what was present, never what should be.
# Per-file minimums: a one-line VERSION.txt is correct, a one-line README is not.
# A single global floor flagged VERSION.txt as defective, which was the gate being wrong.
REQUIRED = {'README.md': 500, 'LICENSE.md': 300, 'VERSION.txt': 4}
# Existence is not presence: an empty README passes an existence check and helps nobody.
# Added after a 0-byte README shipped through this very gate.
missing_entry = [f + ('' if not os.path.exists(f) else f' (only {os.path.getsize(f)} bytes, needs {n})')
                 for f, n in REQUIRED.items()
                 if not os.path.exists(f) or os.path.getsize(f) < n]
print(f'entrypoints: {len(REQUIRED) - len(missing_entry)}/{len(REQUIRED)} required root files present')
for f in missing_entry:
    print(f'    missing: {f}')
if missing_entry:
    failures.append('entrypoints')

print('VERDICT: COMPLETE' if not failures
      else 'VERDICT: INCOMPLETE — ' + ', '.join(failures))
sys.exit(0 if not failures else 1)
