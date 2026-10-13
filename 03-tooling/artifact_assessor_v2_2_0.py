#!/usr/bin/env python3
"""artifact_assessor_v2_2_0.py — capability and maturity OF THE ONTOLOGY.

Supersedes maturity_assessor_v1_0_0.py, which had two defects. It typed its levels as
reliability:CMMIMaturityLevel — CMMI v2.0 ORGANISATIONAL process maturity, a different subject
that shares a word — and it conflated capability with maturity into one score. It also did not
discriminate: 4.6 of 5, four of five dimensions passing for every module.

CAPABILITY — what the vocabulary can DO, scored on ratios so modules can separate:
  answers      competency-question or use-case classes declared
  constrains   SHACL shapes targeting this namespace, per 100 declared classes
  instantiates named individuals per declared class
  composes     owl:imports or cross-namespace properties

MATURITY — how SETTLED it is:
  released     major version reached (>= 1.0.0 scores, >= 2.0.0 scores higher)
  grounded     dcterms:source triples per 100 declared classes
  stable       purpose statement present and not a changelog fragment
  historied    supersession or prior-version records exist

Each scored 0-3, summed to 0-12. ASSESS, NOT CERTIFY: the basis ships with the score.

v2.1.0: the emitted ontology's own rdfs:comment hardcoded "12 subject modules" — the module
COUNT, not the 0-12 scoring scale (that part is genuinely fixed and correctly untouched). Went
silently stale the same way maturity_assessor's summary line did. Now derived from len(rows).

v2.2.0: two directory names were hardcoded to oe-pack's own layout: '01-ontologies' and
'02-shacl-safeguards'. oe-method ships these as '01-vocabularies' and '02-safeguards'. Ran
against oe-method for the first time and hit ZeroDivisionError plus a silent 0-for-shapes on
every module. Both now read from the environment (VOCAB_DIR, SHAPES_DIR), defaulting to
oe-pack's own names.

  python3 artifact_assessor_v2_2_0.py [pack-root] [--emit out.ttl]
"""
import glob
import os
import re
import sys

import rdflib
from rdflib import OWL, RDF, RDFS, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, SKOS

root = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('--') else '.'
emit = sys.argv[sys.argv.index('--emit') + 1] if '--emit' in sys.argv else None
os.chdir(root)
VOCAB_DIR = os.environ.get('VOCAB_DIR', '01-ontologies')
SHAPES_DIR = os.environ.get('SHAPES_DIR', '02-shacl-safeguards')
SH = Namespace('http://www.w3.org/ns/shacl#')
CHANGELOG = re.compile(r'v\d+\.\d+\.\d+|PATCH|MINOR|MAJOR|Sprint|bump|cleanup|retir|absorb', re.I)


def band(v, cuts):
    return sum(1 for c in cuts if v >= c)


shape_count = {}
for f in glob.glob(f'{SHAPES_DIR}/**/*.ttl', recursive=True):
    g = rdflib.Graph()
    try:
        g.parse(f)
    except Exception:
        continue
    for o in g.objects(None, SH.targetClass):
        if isinstance(o, URIRef) and '#' in str(o):
            shape_count[str(o).rsplit('#', 1)[0]] = shape_count.get(str(o).rsplit('#', 1)[0], 0) + 1

rows = []
for f in sorted(glob.glob(f'{VOCAB_DIR}/*_tbox_*.ttl')):
    stem = os.path.basename(f).split('_tbox')[0]
    g = rdflib.Graph(); g.parse(f)
    ont = next(g.subjects(RDF.type, OWL.Ontology), None)
    ns = str(ont)
    ncls = len([c for c in g.subjects(RDF.type, OWL.Class) if isinstance(c, URIRef)]) or 1
    stmt = str(g.value(ont, RDFS.comment) or '')
    ver = str(g.value(ont, OWL.versionInfo) or '0.0.0')
    major = int(re.match(r'(\d+)', ver).group(1)) if re.match(r'\d', ver) else 0

    abox = rdflib.Graph()
    for a in glob.glob(f'{VOCAB_DIR}/{stem}_abox_*.ttl'):
        abox.parse(a)
    inds = len(list(abox.subjects(RDF.type, OWL.NamedIndividual)))
    src = len(list(g.triples((None, DCTERMS.source, None)))) + \
          len(list(abox.triples((None, DCTERMS.source, None))))
    qs = len([c for c in g.subjects(RDF.type, OWL.Class)
              if re.search(r'CompetencyQuestion|UseCase', str(c))])
    imports = len(list(g.objects(ont, OWL.imports)))
    prior = len(list(g.objects(ont, OWL.priorVersion))) + len(list(abox.objects(None, OWL.priorVersion)))

    cap = (band(qs, [1, 2, 4])
           + band(100.0 * shape_count.get(ns, 0) / ncls, [5, 25, 75])
           + band(1.0 * inds / ncls, [0.25, 1.0, 3.0])
           + band(imports, [1, 2, 4]))
    mat = (band(major, [1, 2, 5])
           + band(100.0 * src / ncls, [25, 100, 300])
           + (3 if stmt and not CHANGELOG.search(stmt) and len(stmt) >= 120 else 0)
           + band(prior, [1, 3, 10]))
    rows.append((stem, cap, mat, ncls, qs, shape_count.get(ns, 0), inds, src, imports, major, prior))

print(f'{"module":<24}{"CAP":>4}{"MAT":>5}   classes  cq  shapes  inds  srcs  imp  vmaj  prior')
for r in sorted(rows, key=lambda x: (-x[1], -x[2])):
    print(f'  {r[0]:<22}{r[1]:>4}{r[2]:>5}   {r[3]:>7} {r[4]:>3} {r[5]:>7} {r[6]:>5} {r[7]:>5} {r[8]:>4} {r[9]:>5} {r[10]:>5}')
caps = [r[1] for r in rows]; mats = [r[2] for r in rows]
print(f'\ncapability: mean {sum(caps)/len(caps):.1f}/12, range {min(caps)}-{max(caps)}')
print(f'maturity  : mean {sum(mats)/len(mats):.1f}/12, range {min(mats)}-{max(mats)}')
print(f'DISCRIMINATION: capability spread {max(caps)-min(caps)}, maturity spread {max(mats)-min(mats)}'
      f'  (v1.0.0 spread was 1)')

if emit:
    ACAP = Namespace('http://example.org/artifact-capability#')
    OEL = Namespace('http://example.org/oe-lineage#')
    out = rdflib.Graph(); out.bind('acap', ACAP); out.bind('oel', OEL)
    o = URIRef('http://example.org/oe-lineage/assessment')
    out.add((o, RDF.type, OWL.Ontology)); out.add((o, OWL.versionInfo, Literal('2.2.0')))
    out.add((o, OWL.priorVersion, URIRef('http://example.org/oe-lineage/maturity')))
    out.add((o, RDFS.comment, Literal(
        f'Capability and maturity of the {len(rows)} subject modules discovered at generation time '
        '(re-derive, do not hardcode — v2.0.0 baked in "12" here, and it went silently stale when a '
        '13th module was minted). Scored separately. Supersedes the v1.0.0 assessment, which typed '
        'its levels as reliability:CMMIMaturityLevel — organisational process maturity, not a '
        'property of an ontology — and conflated the two dimensions into one non-discriminating '
        'score. Self-assessment with the basis published, not certification.', lang='en')))
    for i in range(13):
        for kind, cls in (('Capability', ACAP.ArtifactCapabilityLevel), ('Maturity', ACAP.ArtifactMaturityLevel)):
            n = OEL[f'{kind}_L{i}']
            out.add((n, RDF.type, cls)); out.add((n, RDF.type, OWL.NamedIndividual))
            out.add((n, RDFS.label, Literal(f'{kind} level {i} of 12', lang='en')))
    for r in rows:
        a = OEL[f'Assessment2_{r[0]}']
        out.add((a, RDF.type, OWL.NamedIndividual))
        out.add((a, RDFS.label, Literal(f'{r[0]}: capability {r[1]}/12, maturity {r[2]}/12', lang='en')))
        out.add((a, DCTERMS.identifier, Literal(r[0])))
        out.add((a, ACAP.hasCapabilityLevel, OEL[f'Capability_L{r[1]}']))
        out.add((a, ACAP.hasMaturityLevel, OEL[f'Maturity_L{r[2]}']))
        out.add((a, ACAP.hasScoreBasis, Literal(
            f'classes={r[3]} competency/use-case={r[4]} shapes={r[5]} individuals={r[6]} '
            f'dcterms:source={r[7]} imports={r[8]} majorVersion={r[9]} priorVersions={r[10]}. '
            'Re-derive with artifact_assessor_v2_2_0.py.', lang='en')))
    out.serialize(destination=emit, format='turtle')
    print(f'\nwritten: {emit} ({len(out)} triples)')
sys.exit(0)
