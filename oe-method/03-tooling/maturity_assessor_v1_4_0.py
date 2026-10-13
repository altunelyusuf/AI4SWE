#!/usr/bin/env python3
"""maturity_assessor_v1_4_0.py — the capability level of every module of a package, measured by the queries it publishes.

Assigns each module a capability level from evidence present in the artifacts. Every dimension is a property a reader
can re-derive; nothing is scored by opinion.

ASSESS, NOT CERTIFY. Certification implies an authority attesting to an external standard. This is self-assessment by
the body that wrote the criteria, which reliability: names as a conflict of interest — so the output is published WITH
its method, and the method is the claim.

DIMENSIONS (each 0 or 1, level = count), and the level names 0 Declared · 1 Described · 2 Populated · 3 Constrained ·
4 Questioned · 5 Grounded.

v1.4.0: the metric individuals are typed quality:QualityMetric as well as quality:CoverageMetric, because the range
quality:hasMetric declares is QualityMetric and CoverageMetric is not below it.

v1.3.0, three defects, each measured:

(1) THE TOOL READ FILES, AND THE FILES BECAME MODULES. v1.2.0 globbed '<vocab>/*_tbox_*.ttl' and paired each with
    '<stem>_abox_*.ttl'. After the package consolidation (BP-D54) a package ships ONE T-Box and ONE A-Box, so the tool
    found a single pseudo-module named after the package and assessed that: a tool reporting a number for the wrong
    population, which is the same class of defect as its own v1.1.0 note (a hardcoded count going stale). It now
    discovers MODULES through oe_module_lib and still reads the old per-file layout when that is what it finds.

(2) THE SCORE WAS NOT RE-DERIVABLE. The five dimensions were Python expressions; the emitted assessment carried only
    their results. A reader could not dispute the score without reading this file. Now each dimension IS a SPARQL query,
    published on the metric individual as qc:hasSPARQLImplementation and executed here against the package's own corpus:
    the published query and the computed score cannot diverge, because they are one text.

(3) THE EMITTED ASSESSMENT MADE THREE CLAIMS THE FILES DO NOT SUPPORT. v1.2.0 reused quality:QualityAssessment and
    reliability:CMMIMaturityLevel "rather than minting a maturity vocabulary (L-110)". Reuse is right; these two were
    the wrong targets, and nothing caught it because each shape suite was validated only against its own subject's
    files — the lineage A-Box and the measurement shapes never met until the consolidation put them in one run, which
    then showed 65 violations on 13 records. Measured, per L-47's constraint-compatibility extension:
      - quality:QualityAssessment requires qc:assessesArtifact, exactly one qc:appliesAggregationRule, qc:hasMetric
        (whose object must carry qc:hasSPARQLImplementation) and qc:atTimestamp, and its closed shape admits neither
        dcterms:identifier nor a maturity-level predicate. L-47 ranks the mitigations: (a) supply the missing data,
        (b) relax the target constraint, (c) reconsider the target. (a) is taken: every one of those four properties is
        real data this tool already had or can derive — the artifact it assesses is the module, the metrics are the five
        dimension queries, the aggregation rule is their sum, the timestamp is the generation time. dcterms:identifier
        is dropped as redundant with qc:assessesArtifact, which carries the same identity as an IRI.
      - reliability:CMMIMaturityLevel is "canonical CMMI v2.0 organisational maturity level. Five tiers: 1 Initial,
        2 Managed, 3 Defined, 4 Quantitatively Managed, 5 Optimizing". This ladder is 0 Declared … 5 Grounded, measured
        on one ontology module, not an organisation. Same word, different lineage: exactly the claim L-47 and L-75
        forbid asserting from a name. reliability:hasMaturityLevel compounded it — its declared domain is core:Process
        (an assessment record is not a process) and its range is reliability:ReliabilityMaturityLevel (the ladder is
        not one), so under RDFS inference the records claimed to be processes.
      - artifact-capability already holds what this ladder needs and had no individuals at all (its pairing exemption
        in the completeness gate says "ongoing enhancement lineage"): acap:ArtifactCapabilityLevel is "what an ontology
        can DO: which questions it answers, what reasoning it supports, what can be built on it", acap:hasCapabilityLevel
        points at it, and acap:hasScoreBasis exists for "the measured values behind a level, so the score can be
        disputed by re-derivation rather than trusted" — which is the dimension string this tool has always emitted.
        The level ladder is that class's first population (L-71: a class nobody instantiates is the other failure).

The 'shaped' dimension changed its measure with the layout: v1.2.0 asked whether any shape targets a class whose IRI
sits in the module's namespace; it now asks whether any shape targets a class that DECLARES membership of the module.
Post-consolidation membership is the fact and the namespace is the guess, and the two agree on this corpus (verified by
the test, which runs both and compares).

  python3 maturity_assessor_v1_4_0.py [package-root] [--emit out.ttl]

Reads VOCAB_DIR and SHAPES_DIR from the environment (default oe-pack's '01-ontologies' and '02-shacl-safeguards'), so a
package with other folder names needs no edit, and a package holding a second unit (a governance unit with its own
VERSION.txt) is assessed by a second run pointed at that folder.

A record is named after its module's own IRI (its last segment), not after a file stem: the IRI is the identity that
survives a consolidation, and the stem is what disappeared with the files.
"""
import glob
import os
import re
import sys

import rdflib
from rdflib import OWL, RDF, RDFS, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, SKOS, XSD

HERE = os.path.dirname(os.path.abspath(__file__))

ACAP = Namespace('http://example.org/artifact-capability#')
QUA = Namespace('http://example.org/quality#')
MEA = Namespace('http://example.org/measurement#')
OEL = Namespace('http://example.org/oe-lineage#')
SH = Namespace('http://www.w3.org/ns/shacl#')

LEVELS = ['Declared', 'Described', 'Populated', 'Constrained', 'Questioned', 'Grounded']

PREFIXES = """PREFIX acap: <http://example.org/artifact-capability#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sh: <http://www.w3.org/ns/shacl#>
"""

# The five dimensions. Each is the published implementation AND the executed measure: one text, so the score on the
# record and the query a reader runs cannot disagree. $module is bound to the module's IRI.
DIMENSIONS = [
    ('purpose', 'Purpose stated',
     'The module states a purpose of its own: an rdfs:comment of at least 120 characters that is not a change note.',
     PREFIXES + """ASK {
  $module rdfs:comment ?c .
  FILTER(STRLEN(STR(?c)) >= 120)
  FILTER(!REGEX(STR(?c), "v[0-9]+[.][0-9]+[.][0-9]+|PATCH|MINOR|MAJOR|Sprint|bump|cleanup|retir|absorb", "i"))
}"""),
    ('populated', 'Populated',
     'At least one named individual declares membership of the module.',
     PREFIXES + """ASK {
  ?s dcterms:isPartOf $module ;
     a owl:NamedIndividual .
}"""),
    ('shaped', 'Constrained by shapes',
     'At least one SHACL shape targets a class that declares membership of the module.',
     PREFIXES + """ASK {
  ?shape sh:targetClass ?class .
  ?class dcterms:isPartOf $module .
}"""),
    ('questioned', 'Questioned',
     'The module declares at least one competency question or use case class.',
     PREFIXES + """ASK {
  ?c a owl:Class ;
     dcterms:isPartOf $module .
  FILTER(REGEX(STR(?c), "CompetencyQuestion|UseCase"))
}"""),
    ('grounded', 'Grounded in sources',
     'The module carries at least ten dcterms:source rationale triples on its own members. (HAVING without GROUP BY is not honoured by rdflib — measured: it returns false on a count of 29 — so the count is a subquery and the threshold a FILTER.)',
     PREFIXES + """ASK {
  {
    SELECT (COUNT(*) AS ?n) WHERE {
      ?s dcterms:isPartOf $module ;
         dcterms:source ?src .
    }
  }
  FILTER(?n >= 10)
}"""),
]


def load_lib():
    import importlib.util
    cands = sorted(glob.glob(os.path.join(HERE, 'oe_module_lib_v*_*_*.py')),
                   key=lambda p: [int(x) for x in re.findall(r'\d+', os.path.basename(p))])
    if not cands:
        sys.exit('REFUSED: no oe_module_lib copy beside this tool; a module-aware assessment cannot be made')
    sp = importlib.util.spec_from_file_location('oe_module_lib', cands[-1])
    m = importlib.util.module_from_spec(sp)
    sys.modules['oe_module_lib'] = m
    sp.loader.exec_module(m)
    return m


def discover(vocab_dir, shapes_dir, L):
    """[(identifier, module IRI)] plus the corpus they are measured against. Reads the consolidated layout and the
    per-file layout; refuses rather than reporting a level for nothing."""
    corpus = rdflib.Graph()
    files = [f for f in sorted(glob.glob(f'{vocab_dir}/**/*.ttl', recursive=True) +
                               glob.glob(f'{shapes_dir}/**/*.ttl', recursive=True))
             if not re.search(r'/(archive|fixtures?)/', f)]
    for f in files:
        try:
            corpus.parse(f)
        except Exception:
            continue
    mods = []
    for f in sorted(glob.glob(f'{vocab_dir}/*_tbox_*.ttl')):
        g = rdflib.Graph()
        g.parse(f)
        inner = sorted(set(L.module_targets(g)) - set(L.headers(g)))
        if inner:                                                      # consolidated: the file's modules
            for m in inner:
                mods.append((str(m).rstrip('/').rsplit('/', 1)[-1], m))
        else:                                                          # per-file layout: the file IS the module
            ont = next(g.subjects(RDF.type, OWL.Ontology), None)
            if ont is not None:
                mods.append((str(ont).rstrip('/').rsplit('/', 1)[-1], ont))
    if not mods:
        sys.exit(f'REFUSED: no module found under {vocab_dir}; a scan of nothing is not an assessment')
    return mods, corpus


def score(corpus, module):
    d = {}
    for name, _lab, _defn, q in DIMENSIONS:
        d[name] = int(bool(corpus.query(q.replace('$module', f'<{module}>'))))
    return d


def main(argv):
    root = argv[1] if len(argv) > 1 and not argv[1].startswith('--') else '.'
    emit = argv[argv.index('--emit') + 1] if '--emit' in argv else None
    os.chdir(root)
    vocab_dir = os.environ.get('VOCAB_DIR', '01-ontologies')
    shapes_dir = os.environ.get('SHAPES_DIR', '02-shacl-safeguards')
    L = load_lib()
    mods, corpus = discover(vocab_dir, shapes_dir, L)
    rows = []
    for ident, module in mods:
        d = score(corpus, module)
        rows.append((ident, module, sum(d.values()), d))
    print(f'{"module":<24} {"level":<26} pur pop shp que gnd')
    for ident, module, lvl, d in rows:
        print(f'  {ident:<22} {lvl} {LEVELS[lvl]:<22}' + ' '.join(f'  {v}' for v in d.values()))
    print(f'\nassessed: {len(rows)} modules · mean level {sum(r[2] for r in rows) / len(rows):.1f} of 5'
          f' · corpus {len(corpus)} triples')
    low = [r[0] for r in rows if r[2] <= 2]
    if low:
        print(f'at or below Populated: {", ".join(low)}')
    if not emit:
        return 0

    import datetime
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')
    out = rdflib.Graph()
    out.bind('acap', ACAP); out.bind('qua', QUA); out.bind('mea', MEA); out.bind('oel', OEL)
    o = URIRef('http://example.org/oe-lineage/maturity')
    out.add((o, RDF.type, OWL.Ontology))
    out.add((o, OWL.versionInfo, Literal('1.3.0')))
    out.add((o, RDFS.comment, Literal(
        f'Capability assessment of the {len(rows)} modules discovered at generation time (re-derive, do not hardcode — '
        'a prior version of this tool baked in "12" here and in its own summary line, and both went stale silently when '
        'a 13th module was minted; the version after that read files and found one pseudo-module once the package was '
        'consolidated). Each level is the count of five dimensions, and each dimension is the SPARQL query published on '
        'its metric: the query is the implementation, so the score cannot drift from its method. Reuses '
        'acap:ArtifactCapabilityLevel, acap:hasCapabilityLevel and acap:hasScoreBasis, which exist for exactly this and '
        'had no individuals (L-71), rather than minting a vocabulary (L-110); the previous version reused '
        'quality:QualityAssessment correctly but also reliability:CMMIMaturityLevel, an organisational CMMI tier, which '
        'this ladder is not (L-47, L-75). Self-assessment, not certification: the method is published with the result '
        'so a reader can dispute the score by re-deriving it.', lang='en')))

    rule = OEL['Rule_CapabilityDimensionCount_v1_0_0']
    out.add((rule, RDF.type, MEA.AggregationRule)); out.add((rule, RDF.type, OWL.NamedIndividual))
    out.add((rule, RDFS.label, Literal('Capability dimension count', lang='en')))
    out.add((rule, SKOS.definition, Literal(
        'The capability level is the unweighted count of the five dimensions that hold: purpose, populated, shaped, '
        'questioned, grounded. Each dimension contributes 0 or 1 and none is weighted above another, so the level is '
        'an integer from 0 to 5 and a reader can recompute it from the five dimension queries alone.', lang='en')))
    out.add((rule, DCTERMS.source, Literal('maturity_assessor_v1_4_0.py, the tool that emits this file; the five '
                                           'dimension queries are published on the metrics it references.')))
    out.add((rule, DCTERMS.isPartOf, o))

    metrics = {}
    for name, lab, defn, q in DIMENSIONS:
        mi = OEL[f'Metric_Capability_{name.capitalize()}_v1_0_0']
        metrics[name] = mi
        # Both classes, deliberately: quality:hasMetric declares its range as quality:QualityMetric (the home's own
        # declaration, after the duplicate declarations were withdrawn), and quality:CoverageMetric is not a subclass of
        # it -- the two sit side by side under measurement:Measurement. A metric that is only a CoverageMetric would
        # make every hasMetric triple pointing at it false. Every predicate emitted here is inside the closed
        # QualityMetric shape's whitelist, which was checked before adding the type, not after.
        out.add((mi, RDF.type, QUA.CoverageMetric)); out.add((mi, RDF.type, QUA.QualityMetric))
        out.add((mi, RDF.type, OWL.NamedIndividual))
        out.add((mi, RDFS.label, Literal(f'Capability dimension: {lab}', lang='en')))
        out.add((mi, SKOS.definition, Literal(defn + ' Measured as 0 or 1 by the query in '
                                              'qc:hasSPARQLImplementation, with $module bound to the module assessed.',
                                              lang='en')))
        out.add((mi, QUA.hasSPARQLImplementation, Literal(q)))
        out.add((mi, DCTERMS.source, Literal('maturity_assessor_v1_4_0.py: this query is the executed measure, not a '
                                             'description of one.')))
        out.add((mi, RDFS.isDefinedBy, o))
        out.add((mi, DCTERMS.isPartOf, o))

    for i, name in enumerate(LEVELS):
        n = OEL[f'Level_{i}_{name}']
        out.add((n, RDF.type, ACAP.ArtifactCapabilityLevel)); out.add((n, RDF.type, OWL.NamedIndividual))
        out.add((n, RDFS.label, Literal(f'{i} — {name}', lang='en')))
        out.add((n, SKOS.definition, Literal(
            f'Capability level {i} of 5: {i} of the five dimensions hold. The ladder is 0 Declared, 1 Described, '
            '2 Populated, 3 Constrained, 4 Questioned, 5 Grounded, and it describes one ontology module, not an '
            'organisation.', lang='en')))
        out.add((n, DCTERMS.isPartOf, o))

    for ident, module, lvl, d in rows:
        a = OEL[f'Assessment_{ident}']
        out.add((a, RDF.type, QUA.QualityAssessment)); out.add((a, RDF.type, OWL.NamedIndividual))
        out.add((a, RDFS.label, Literal(f'{ident}: level {lvl} ({LEVELS[lvl]})', lang='en')))
        out.add((a, SKOS.definition, Literal(
            f'purpose={d["purpose"]} populated={d["populated"]} shaped={d["shaped"]} questioned={d["questioned"]} '
            f'grounded={d["grounded"]}; level {lvl} of 5. Re-derive by running the five queries published on the '
            'metrics this assessment references, with $module bound to the assessed module.', lang='en')))
        out.add((a, QUA.assessesArtifact, module))
        out.add((a, QUA.appliesAggregationRule, rule))
        for name in d:
            out.add((a, QUA.hasMetric, metrics[name]))
        out.add((a, QUA.atTimestamp, Literal(now, datatype=XSD.dateTime)))
        out.add((a, ACAP.hasCapabilityLevel, OEL[f'Level_{lvl}_{LEVELS[lvl]}']))
        out.add((a, ACAP.hasScoreBasis, Literal(
            f'purpose={d["purpose"]} populated={d["populated"]} shaped={d["shaped"]} questioned={d["questioned"]} '
            f'grounded={d["grounded"]}')))
        out.add((a, DCTERMS.isPartOf, o))

    out.serialize(destination=emit, format='turtle')
    print(f'\nassessment written: {emit} ({len(out)} triples)')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
