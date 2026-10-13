#!/usr/bin/env python3
"""release_check_v3_2_0.py — a release gate that cannot pass on an empty set.

WHY THIS IS A REWRITE, NOT A PATCH
  v1.7.0 hard-coded MANIFEST_SHA256.txt, 01-ontologies/ and 02-shacl-safeguards/. Derived into a
  package with any other convention it reported "0/0 OK" and "no kb shacl shipped" — passing, or
  failing quietly, on nothing. Four successive patches each fixed one path and exposed the next,
  which is the signature of a structural defect rather than a series of bugs.

THE RULE THIS ENFORCES ON ITSELF
  Every discovery step must yield at least one artifact, or the gate FAILS and says which step
  found nothing. A check that ran against zero files is not a pass; it is an absence of evidence
  reported as evidence of absence — the decorative-verification failure the catalogue already
  names, committed by the instrument itself.

v3.0.0 (OEE consolidation, P2): reads BOTH layouts. A package of one file per role keeps its former subjects as MODULES (BP-D54); the shape suites are then
modules of one SHACL file, and "a suite is validated against its own subject" becomes "a module's shapes are validated against the modules of the T-Box and
A-Box that carry the same dcterms:identifier" (the file-name stem of the old layout), plus the same additional subjects the config names. The slice of a
module is its members and their blank-node closure (oe_module_lib), with the module resource itself for sh:prefixes and sh:declare. The finding set of every suite is
the same in both layouts (proved on the OE pack: oe_release_check_layout_test). The full-corpus suite named in the config stays deferred. With one file per role
the old pairing by file-name stem would have run the single suite against everything; that is why this reading exists.

DISCOVERY
  manifest   the highest-SemVer MANIFEST_SHA256*.txt anywhere in the package
  ontologies the directory containing the most *_tbox_*.ttl / *_abox_*.ttl files
  shapes     files that actually declare a real sh:NodeShape (parsed, not text-matched — v2.1.0)
  discipline (v2.3.0) the highest-SemVer OE_Operating_Discipline_v*.md in this package's own
             04-documentation/, compared against oe-method's, when a sibling checkout is present.
             Real cross-session finding (2026-09-07): this file existed in two byte states under
             the identical version token — the ceremony's own pointer-resolution rule treats it
             as identically shared across packages, unlike ordinary tbox/abox/tool content, which
             is EXPECTED to diverge under LINEAGE.tsv's own 'generalised' derivation. A blanket
             same-basename-must-match rule was considered and rejected: it would false-positive on
             every legitimately generalised file. Narrowed to this one artifact by design, not by
             oversight. FAILS only when the token is identical AND the bytes differ — a declared
             divergence (different tokens) is not a violation. Tested against a simulated repeat
             of the original bug before shipping (L-95): same token, different bytes, correctly FAILS.
  Deposits of other parties' packages, negative fixtures, and 06-audit-artifacts (explicitly
  disposed, preserved-not-live snapshots) are excluded from every scan.

v2.1.0 (F-SH4, KNOWN_FINDINGS_v20_37_0.md): shape discovery previously text-matched "NodeShape"
  anywhere in a file, producing 2 false positives (narrative prose mentioning past NodeShapes,
  0 real ones). Now parses and checks for an actual sh:NodeShape triple. Added explicit
  suite-to-subject declarations for suites whose constraints are inherently cross-vocabulary
  (redo_shacl needs the full 28-file corpus; reliability_shacl additionally needs configuration
  data) rather than relying solely on filename-stem inference, per KNOWN_FINDINGS' own
  recommendation. The full-corpus suite is deferred from the fast path (documented, not silent)
  since validating ~1967 individuals via SPARQL exceeds this environment's per-call time budget
  even though it completes standalone — see F_SH4_redo_shacl_full_corpus_v1_0_0.md for its
  last-verified result.

v2.2.0 (Obj_Configurability, T6.1.1): the 4 points that varied per invocation — the exclusion
  regex and the three suite-subject structures above — were inline Python literals through
  v2.1.0, requiring a source edit to change any of them. Now loaded from a sibling JSON file,
  release_check_config_v1_4_0.json, overridable via the RELEASE_CHECK_CONFIG environment
  variable. Behaviour-preserving by construction: the shipped config carries the exact v2.1.0
  defaults, verified with the identical gate result (manifest, parse, pairing and violation
  counts unchanged) before and after this change, in the same turn.

  v2.4.0 (2026-10-05): the config names suites by STEM (redo_shacl, reliability_shacl), not by exact file
  name. Splitting mixed-role files (BP-D53) gave two SHACL files new versions, and a config keyed by exact
  file name then silently stopped applying (a suite would have fallen back to the narrow subject list that
  produced 48 spurious violations). A stem matches every version of that file; an exact name still matches.

  python3 release_check_v2_4_0.py [package-root]
"""
import glob
import hashlib
import json
import os
import re
import sys

# v2.2.0 (Obj_Configurability, T6.1.1): the 4 points below were inline Python literals through
# v2.1.0 — no way to change them without editing this file. Now loaded from a sibling JSON config,
# overridable via RELEASE_CHECK_CONFIG. Defaults preserve every v2.1.0 value exactly (verified:
# same manifest/parse/pairing/violation counts before and after this change, same turn).
_CONFIG_PATH = os.environ.get(
    'RELEASE_CHECK_CONFIG',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'release_check_config_v1_4_0.json'))
with open(_CONFIG_PATH, encoding='utf-8') as _cf:
    _CONFIG = json.load(_cf)

# v3.2.0 (plan v1.13.0 item 48): a module's suite may carry a RECORDED CEILING of violations (config key `recorded_suite_violations`, keyed by the
# shape module's IRI). Needed when a unit holds another party's data and shapes (the registrations): the party's own shapes may find
# things in its own data that this package cannot fix. Up to the recorded number the findings are reported as recorded and do not fail
# the gate; above it they fail; below it the run says the ceiling can be lowered. It is the same ratchet as the structure debt register:
# a number that can only fall. No key means no ceiling, so nothing else changes.
# v3.1.0 (plan v1.10.0 item 38(b)): what this gate does not read comes from the ONE class table (OE_STRUCTURE_CLASSES_v*.tsv,
# 04-documentation of the package), through oe_structure_classes_v*.py, which the structure check and the publisher also use.
# The earlier pattern in the config skipped by WORDS in names (negative, invalid, _bad_...), so a real file called
# ..._invalid_... would have been skipped without a word; the table skips whole folders and nothing else. A config that still
# carries `exclude_pattern` is told that it is no longer read.
EXCLUDE = None     # set below, once the package root is known
                     # v2.1.0: 06-audit-artifacts added. Its one file, redo_v3_0_0.ttl, carries
                     # its own recorded disposition (oepack_release_history v20.8.0, orh:ReleaseEvent
                     # Step-4 KM closure): "PRESERVATION: full definitions + academic provenance
                     # retained ... retrievable verbatim if a need materializes" — an explicitly
                     # archived snapshot, not live corpus. It has 29 real sh:NodeShape declarations
                     # (confirmed by parsing, not the substring check this version replaces) and was
                     # surfacing as F-SH4 "unpaired" only because discovery walked archives too.


def keep(p):
    return not EXCLUDE.search('/' + p.replace(os.sep, '/'))


def all_files(pat='**/*'):
    return [p for p in glob.glob(pat, recursive=True) if os.path.isfile(p) and keep(p)]


_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
_libs = sorted(glob.glob(os.path.join(_HERE, 'oe_module_lib_v*.py')), key=lambda p: [int(x) for x in re.findall(r'\d+', os.path.basename(p))])
if _libs:
    import importlib.util as _iu
    _sp = _iu.spec_from_file_location('oe_module_lib', _libs[-1]); LIB = _iu.module_from_spec(_sp); _sp.loader.exec_module(LIB)
else:
    LIB = None
root = sys.argv[1] if len(sys.argv) > 1 else '.'
os.chdir(root)
_cl = sorted(glob.glob(os.path.join(_HERE, 'oe_structure_classes_v*.py')), key=lambda p: [int(x) for x in re.findall(r'\d+', os.path.basename(p))])
if not _cl:
    raise SystemExit('REFUSED: oe_structure_classes_v*.py is missing next to this gate; it is the one reader of the class table')
_sc = _iu.spec_from_file_location('oe_structure_classes', _cl[-1]); CLASSES = _iu.module_from_spec(_sc); _sc.loader.exec_module(CLASSES)
TABLE = CLASSES.load('.')
EXCLUDE = TABLE.release_exclude()
print(f'== release gate v3.2.0 on: {os.getcwd()} ==')
print('-- class table: ' + (os.path.basename(TABLE.path) if TABLE.path else 'NOT FOUND, the built-in copy of the earlier lists is used (04-documentation/OE_STRUCTURE_CLASSES_v*.tsv)'))
if 'exclude_pattern' in _CONFIG:
    print('-- NOTICE: the config still carries exclude_pattern; it is no longer read, the class table decides')

failures = []
empty = []


def step(name, found, detail=''):
    """A discovery yielding nothing is a FAILURE, never a pass."""
    if not found:
        print(f'-- {name}: NOTHING DISCOVERED — cannot verify what is not there')
        empty.append(name)
        failures.append(name)
        return False
    print(f'-- {name}: {detail}')
    return True


# ---- 1. manifest -----------------------------------------------------------
mans = sorted([p for p in all_files('**/MANIFEST_SHA256*.txt')], key=lambda p: [
    int(n) for n in re.findall(r'\d+', os.path.basename(p))] or [0])
if step('manifest discovery', mans, f'{os.path.basename(mans[-1])}' if mans else ''):
    mf = mans[-1]
    base = os.path.dirname(mf) or '.'
    ok = n = 0
    for line in open(mf, encoding='utf-8', errors='replace'):
        m = re.match(r'^([0-9a-fA-F]{64})\s+\*?(\S.*?)(?:\s+\(\d+b\))?$', line.strip())
        if not m:
            continue
        n += 1
        p = os.path.join(base, m.group(2))
        try:
            ok += hashlib.sha256(open(p, 'rb').read()).hexdigest() == m.group(1)
        except OSError:
            pass
    if n == 0:
        print('   manifest lists NO entries — a manifest that covers nothing verifies nothing')
        failures.append('manifest empty')
    else:
        print(f'   {ok}/{n} OK')
        if ok != n:
            failures.append('manifest mismatch')

# ---- 2. ontologies ---------------------------------------------------------
tboxes = [p for p in all_files('**/*_tbox_*.ttl')]
aboxes = [p for p in all_files('**/*_abox_*.ttl')]
onto = tboxes + aboxes
if step('ontology discovery', onto, f'{len(tboxes)} TBox, {len(aboxes)} ABox'):
    try:
        import rdflib
    except ImportError:
        print('   rdflib absent — cannot parse'); failures.append('toolchain')
        rdflib = None
    if rdflib:
        bad = []
        for f in sorted(set(onto)):
            try:
                rdflib.Graph().parse(f)
            except Exception as e:
                bad.append((f, str(e)[:60]))
        print(f'   parse {len(set(onto)) - len(bad)}/{len(set(onto))} OK')
        for b in bad[:5]:
            print(f'     PARSE FAIL {b[0]}: {b[1]}')
        if bad:
            failures.append('parse')

# ---- 3. shapes -------------------------------------------------------------
# v2.1.0: shape discovery now PARSES each candidate and checks for a real `?s a sh:NodeShape`
# triple, instead of a substring search for the text "NodeShape" anywhere in the file. The
# substring check produced two false positives (prov_phase_1_v1_0_0.ttl, prov_phase_2_v1_0_0.ttl
# in 05-prov-records/) whose only "NodeShape" occurrence was narrative prose describing a past
# deliverable ("29 NodeShapes extracted from...") — zero actual shapes, confirmed by parsing.
SHACL_NS = 'http://www.w3.org/ns/shacl#'
candidates = [p for p in all_files('**/*.ttl') if 'NodeShape' in open(p, encoding='utf-8', errors='replace').read()]
shapes = []
try:
    import rdflib as _rdflib_probe
except ImportError:
    _rdflib_probe = None
if _rdflib_probe:
    for p in candidates:
        try:
            g = _rdflib_probe.Graph()
            g.parse(p)
            if (None, _rdflib_probe.RDF.type, _rdflib_probe.URIRef(SHACL_NS + 'NodeShape')) in g:
                shapes.append(p)
        except Exception:
            pass
else:
    shapes = candidates  # toolchain absent; fall back to the old (over-inclusive) behaviour

# Explicit suite-to-subject declarations (KNOWN_FINDINGS_v20_37_0.md F-SH4: "an explicit
# suite-to-ontology declaration would be sounder than inferring it from names"). Filename-stem
# pairing still runs first; this only covers suites the stem heuristic cannot resolve because
# their filename predates a rename/absorption in the vocabulary they target.
def _stem(name):
    return re.sub(r'_v\d+_\d+_\d+\.ttl$', '', name)
def _keyed(d):
    return {_stem(k): v for k, v in d.items()}
SUITE_SUBJECT_OVERRIDE_FULL_CORPUS = {_stem(k) for k in _CONFIG['suite_subject_override_full_corpus']}
# redo_shacl's constraints (C7+ type-declaration checking, C2/C2+/C3/D3+ annotation-completeness)
# are inherently cross-vocabulary by design — C7+ explicitly checks whether an rdf:type is
# declared ANYWHERE reachable, not just locally. Validating it against a narrow subject list
# (even the correct reliability/measurement/configuration namespaces its shapes target)
# produced 48 spurious violations — individuals correctly typed by classes declared in
# OTHER files the narrow list excluded (oqc-measurements classes live in quality_tbox, not
# reliability/measurement/configuration). Against the full 28-file corpus: 3 genuine
# violations (reliability:FailureMode, reliability:Risk used as rdf:type on real individuals,
# never declared as owl:Class anywhere) — down from 48. Confirmed by direct reproduction
# before shipping this override, not assumed from the count alone.
SUITE_SUBJECT_OVERRIDE = _keyed(_CONFIG['suite_subject_override'])
# (kept empty for filename-stem-unresolvable suites needing a SPECIFIC subject list;
# none currently need this — redo_shacl needs the full corpus instead, handled above)

# Suites whose OWN filename stem resolves fine, but whose constraints still reach into another
# vocabulary's data — additive, so it applies even when `subj` is already non-empty.
SUITE_SUBJECT_ADDITIONAL = _keyed(_CONFIG['suite_subject_additional'])
# reliability_shacl_v8_0_0.ttl -> ['configuration_tbox_', 'configuration_abox_']:
# C6PROVOManifestShape needs configuration data even though reliability_shacl's own stem
# match already resolves (to reliability_tbox+abox). Both reliability:hasManifest and
# configuration:declaredInManifest declare rdfs:range configuration:SprintManifest, so RDFS
# inference derives SprintManifest targets from reliability data alone — but the
# artefact-evidence triples that would satisfy C6 for those targets live only in
# configuration_abox. Without this, the fast path perpetually reports
# configuration:USO_Sprint12_Manifest as failing C6 even after the underlying data is fixed
# (F-SH3), because it never loads the fix. Confirmed by direct reproduction: reliability-only
# -> 1 violation (stale, pre-fix state); reliability+configuration -> 1 violation, but a
# DIFFERENT target reached only via RDFS range inference from
# configuration:declaredInManifest, never explicitly typed as SprintManifest anywhere — a
# new, genuine, previously-undiscovered finding (see F-SH5 in the closure record), not
# something this fix papers over.

if step('shape discovery', shapes, f'{len(shapes)} file(s) declaring sh:NodeShape'):
    try:
        import pyshacl, rdflib
        data = rdflib.Graph()
        for f in sorted(set(onto)):
            try:
                data.parse(f)
            except Exception:
                pass
        # Each suite is validated against ITS OWN subject, paired by filename stem. Validating
        # every suite against every ontology is O(n^2) and timed out at 33 x 111; it is also less
        # meaningful, since a suite constrains the vocabulary it was written for.
        ran = errs = viol = skipped = deferred = 0
        ogs = {}
        if LIB is not None:
            for o in sorted(set(onto)):
                try:
                    ogs[o] = rdflib.Graph(); ogs[o].parse(o)
                except Exception:
                    ogs.pop(o, None)
        from rdflib import Literal as _Lit, URIRef as _URI

        _pairs = _CONFIG.get('module_pairs', {})
        _more = _CONFIG.get('suite_subject_additional_modules', {})
        _full = set(_CONFIG.get('full_corpus_modules', []))
        _recorded = _CONFIG.get('recorded_suite_violations', {})
        recorded_seen = 0

        def _canon(iri):
            return _pairs.get(str(iri), str(iri))

        _FIND = {}
        _FIND_PATH = os.environ.get('RELEASE_CHECK_FINDINGS')

        def validate(dg, sg, key=None):
            conf, rg, txt = pyshacl.validate(data_graph=dg, shacl_graph=sg, inference='rdfs', advanced=True)
            if _FIND_PATH and key:
                SH = rdflib.Namespace(SHACL_NS); S = set()
                for r in rg.subjects(rdflib.RDF.type, SH.ValidationResult):
                    g_ = lambda p_: str(rg.value(r, p_))
                    S.add((g_(SH.focusNode), g_(SH.sourceShape), g_(SH.sourceConstraintComponent), g_(SH.resultPath), g_(SH.resultSeverity)))
                _FIND[key] = sorted(S)
            return txt.count('Severity: sh:Violation')

        for f in sorted(shapes):
            sg = rdflib.Graph()
            try:
                sg.parse(f)
            except Exception as e:
                errs += 1; print(f'   SUITE ERROR {os.path.basename(f)}: {str(e)[:60]}'); continue
            smods = sorted(LIB._module_resources(sg), key=str) if LIB is not None else []
            if smods:
                # CONSOLIDATED layout: one suite per module of this file
                print(f'   {os.path.basename(f)}: consolidated, {len(smods)} module(s)')
                for sm in smods:
                    ident = str(sm).replace('http://example.org/', '')
                    sshapes = LIB.slice(sg, sm)
                    if not len(sshapes):
                        print(f'   module {ident}: no members (a record of a former header), nothing to run'); continue
                    if str(sm) in _full:
                        deferred += 1
                        print(f'   module {ident}: RESOLVED to full corpus, deferred from fast path (see F_SH4_redo_shacl_full_corpus_v1_0_0.md)')
                        continue
                    wanted = {_canon(sm)} | {_canon(x) for x in _more.get(str(sm), [])}
                    d2 = rdflib.Graph()
                    for o, og in ogs.items():
                        for m in LIB._module_resources(og):
                            if _canon(m) in wanted:
                                for tr in LIB.slice(og, m): d2.add(tr)
                    if not len(d2):
                        skipped += 1; print(f'   no subject module for {ident} — suite not run'); continue
                    for tr in sg.triples((sm, None, None)): sshapes.add(tr)
                    for pfx, ns in sg.namespaces(): sshapes.bind(pfx, ns, override=False)
                    try:
                        n_ = validate(d2, sshapes, _canon(sm))
                    except Exception as e:
                        errs += 1; print(f'   SUITE ERROR {ident}: {str(e)[:60]}'); continue
                    ran += 1
                    rec_ = int(_recorded.get(str(sm), 0))
                    viol += max(0, n_ - rec_)
                    if rec_:
                        recorded_seen += min(n_, rec_)
                        print(f'   module {ident}: {n_} violation(s), {rec_} recorded' + (f'; {n_ - rec_} NEW' if n_ > rec_ else ('; BELOW the recorded ceiling, lower it in the config' if n_ < rec_ else '; at the recorded ceiling')))
                    if os.environ.get('RELEASE_CHECK_VERBOSE'): print(f'   SUITE {ident} {n_}')
                continue
            stem = re.split(r'_(shacl|shapes)', os.path.basename(f))[0]
            subj = [o for o in set(onto) if os.path.basename(o).startswith(stem)]
            if not subj and _stem(os.path.basename(f)) in SUITE_SUBJECT_OVERRIDE:
                prefixes = SUITE_SUBJECT_OVERRIDE[_stem(os.path.basename(f))]
                subj = [o for o in set(onto) if any(os.path.basename(o).startswith(pfx) for pfx in prefixes)]
            if _stem(os.path.basename(f)) in SUITE_SUBJECT_ADDITIONAL:
                extra_pfx = SUITE_SUBJECT_ADDITIONAL[_stem(os.path.basename(f))]
                extra = [o for o in set(onto) if any(os.path.basename(o).startswith(pfx) for pfx in extra_pfx)]
                subj = sorted(set(subj) | set(extra))
            if not subj and _stem(os.path.basename(f)) in SUITE_SUBJECT_OVERRIDE_FULL_CORPUS:
                deferred += 1
                print(f'   {os.path.basename(f)}: RESOLVED to full corpus, deferred from fast path '
                      f'(see F_SH4_redo_shacl_full_corpus_v1_0_0.md)')
                continue
            if not subj:
                skipped += 1
                print(f'   no subject ontology for {os.path.basename(f)} — suite not run')
                continue
            d2 = rdflib.Graph()
            for o in subj:
                try:
                    d2.parse(o)
                except Exception:
                    pass
            try:
                n_ = validate(d2, sg, os.path.basename(f))
            except Exception as e:
                errs += 1
                print(f'   SUITE ERROR {os.path.basename(f)}: {str(e)[:60]}')
                continue
            ran += 1
            viol += n_
            if os.environ.get('RELEASE_CHECK_VERBOSE'): print(f'   SUITE {_stem(os.path.basename(f))} {n_}')
        if _FIND_PATH:
            json.dump(_FIND, open(_FIND_PATH, 'w'))
        print(f'   suites run {ran}/{ran + skipped + deferred + errs} ({skipped} unpaired, {deferred} resolved-but-deferred, '
              f'{errs} errored), violations {viol}' + (f' (+{recorded_seen} recorded)' if recorded_seen else ''))
        if viol:
            failures.append('shacl')
        if errs:
            failures.append('shacl suite error')
        if ran == 0:
            failures.append('shacl: no suite could run')
    except ImportError:
        print('   pyshacl absent'); failures.append('toolchain')

# ---- 4. cross-package discipline consistency -------------------------------
# A real cross-session finding (2026-09-07): OE_Operating_Discipline_v2_5_0.md existed in two
# byte states -- oe-pack's real one, oe-method's generalised one -- under the identical version
# token. This is the ONE artifact the ceremony's own pointer-resolution rule treats as
# identically shared across packages ("resolve to the highest-versioned... in the attached OE
# Pack"), unlike ordinary tbox/abox/tool content, which is EXPECTED to diverge under
# LINEAGE.tsv's own 'generalised' derivation and would false-positive under a blanket
# same-basename-must-match rule -- checked and rejected as the design for this reason before
# writing the narrower check below.
sibling = os.path.join(os.path.dirname(os.getcwd()), 'oe-method', '04-documentation')
if os.path.isdir(sibling):
    my_disc = sorted(glob.glob('04-documentation/OE_Operating_Discipline_v*.md'),
                      key=lambda p: [int(x) for x in re.findall(r'\d+', p)])
    their_disc = sorted(glob.glob(os.path.join(sibling, 'OE_Operating_Discipline_v*.md')),
                         key=lambda p: [int(x) for x in re.findall(r'\d+', p)])
    if my_disc and their_disc:
        mine, theirs = my_disc[-1], their_disc[-1]
        my_tok = re.search(r'_v(\d+_\d+_\d+)\.md$', mine).group(1)
        their_tok = re.search(r'_v(\d+_\d+_\d+)\.md$', theirs).group(1)
        if my_tok == their_tok:
            with open(mine, 'rb') as f:
                mb = f.read()
            with open(theirs, 'rb') as f:
                tb = f.read()
            if mb != tb:
                print(f'-- discipline consistency: FAIL — {os.path.basename(mine)} carries different '
                      f'bytes in oe-pack and oe-method under the identical token {my_tok}')
                failures.append('discipline-consistency')
            else:
                print(f'-- discipline consistency: {os.path.basename(mine)} byte-identical in both packages')
        else:
            print(f'-- discipline consistency: tokens differ ({my_tok} vs {their_tok}) — '
                  f'declared divergence, not a silent one, not a violation')
    else:
        print('-- discipline consistency: SKIPPED — no OE_Operating_Discipline found in one side')
else:
    print('-- discipline consistency: SKIPPED — no sibling oe-method checkout found')

# ---- verdict ---------------------------------------------------------------
if empty:
    print(f'\n*** {len(empty)} discovery step(s) found nothing: {", ".join(empty)}')
    print('    This is a FAIL, not a pass. A gate reporting OK on an empty set is decorative.')
print('== RELEASE GATE: PASS ==' if not failures
      else '== RELEASE GATE: FAIL — ' + ', '.join(sorted(set(failures))) + ' ==')
sys.exit(0 if not failures else 1)
