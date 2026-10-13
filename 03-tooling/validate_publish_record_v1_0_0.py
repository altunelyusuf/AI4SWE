#!/usr/bin/env python3
"""Validate a publish record against the ceremony shape.

Exits 0 only if the record conforms with zero violations. Used by oe_publish_v*.sh
before anything is pushed, and by CI over every PUBLISH_RECORD.ttl in the repo.
"""
import sys
import rdflib
import pyshacl

record, shapes = sys.argv[1], sys.argv[2]
data = rdflib.Graph().parse(record, format='turtle')
shp = rdflib.Graph().parse(shapes, format='turtle')
conforms, _, text = pyshacl.validate(
    data_graph=data, shacl_graph=shp, inference='rdfs', advanced=True)
violations = text.count('Severity: sh:Violation')
print(f"ceremony shape: conforms={conforms} violations={violations}")
if not conforms:
    for line in text.splitlines():
        if 'Message:' in line or 'Focus Node' in line or 'Value Node' in line:
            print("   " + line.strip())
sys.exit(0 if conforms else 1)
