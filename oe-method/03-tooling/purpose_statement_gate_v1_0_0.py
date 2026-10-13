#!/usr/bin/env python3
"""purpose_statement_gate_v1_0_0.py — OEL-T1.1.4.

A module's ontology-level rdfs:comment is the first thing any reader, any generated document and
any enhancement search reads. Measured 2026-08-11: all 12 subject modules carried a changelog
fragment there instead — quality: read "quality PATCH v4.1.1. Sprint F1 ghost-reference cleanup".
Provenance in the field where purpose belongs.

FAILS a module whose statement matches the changelog pattern, or is too short to be a purpose,
or asserts a count without citing how to reproduce it.

  python3 purpose_statement_gate_v1_0_0.py [ontologies-dir]
"""
import glob
import os
import re
import sys

import rdflib
from rdflib import OWL, RDF, RDFS

CHANGELOG = re.compile(
    r'v\d+\.\d+\.\d+|PATCH|MINOR|MAJOR|Sprint|bump|cleanup|retir|absorb|step \d|'
    r'dangling|ghost-reference|consolidat\w+ arc|folded into', re.I)
COUNT = re.compile(r'\b\d{2,}\b')
MIN_CHARS = 120

root = sys.argv[1] if len(sys.argv) > 1 else '01-ontologies'
rows, failures = [], []

for f in sorted(glob.glob(os.path.join(root, '*_tbox_*.ttl'))):
    g = rdflib.Graph()
    g.parse(f)
    ont = next(g.subjects(RDF.type, OWL.Ontology), None)
    stmt = str(g.value(ont, RDFS.comment) or '')
    name = os.path.basename(f).split('_tbox')[0]
    why = []
    if CHANGELOG.search(stmt):
        why.append(f'changelog marker "{CHANGELOG.search(stmt).group(0)}"')
    if len(stmt) < MIN_CHARS:
        why.append(f'{len(stmt)} chars, under {MIN_CHARS}')
    if COUNT.search(stmt) and 'reproduce' not in stmt.lower() and 'count' not in stmt.lower():
        why.append('asserts a figure without saying how to reproduce it')
    rows.append((name, why))
    if why:
        failures.append(name)

for name, why in rows:
    print(f'  {"FAIL" if why else "ok  "} {name:<24} {"; ".join(why)}')
print(f'purpose statements: {len(rows) - len(failures)}/{len(rows)} state a purpose')
print('VERDICT: PURPOSEFUL' if not failures else f'VERDICT: CHANGELOG-IN-PURPOSE-FIELD — {len(failures)} module(s)')
sys.exit(0 if not failures else 1)
