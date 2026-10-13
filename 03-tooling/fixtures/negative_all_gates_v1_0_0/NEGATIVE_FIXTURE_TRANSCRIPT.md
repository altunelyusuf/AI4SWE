# Negative fixture transcript — all three gates, one tree

Real output from running each gate against this fixture, captured directly, not written from
memory of what should happen.

## Lineage gate — run directly against this fixture's own path

```
declared   : 1 derived, 4 original, 0 undeclared
drift      : 0/1 derived files match the transform of their current source
    ORPHANED: 01-vocabularies/orphan_tbox_v1_0_0.ttl  <- pack:01-ontologies/orphan_tbox_v1_0_0.ttl no longer exists upstream
unmapped   : 0 upstream files in declared scope with no entry here
VERDICT: OUT OF ACCORDANCE — orphaned
```

## Completeness gate — run directly against this fixture's own path

```
population : 0/1 classes populated (0.0%), 1 leaf classes with no individual
    orphan_tbox_v1_0_0.ttl: Widget
    below recorded baseline of 39.0%
pairing    : 0/1 vocabularies ship both TBox and ABox, or are exempted (BP-D51)
    no ABox for: orphan
protocol   : protocol doc=False publisher=False
shapes     : 0/1 vocabularies have shape coverage
    no shapes targeting: http://example.org/orphan
entrypoints: 1/3 required root files present
    missing: LICENSE.md
    missing: VERSION.txt
VERDICT: INCOMPLETE — population, pairing, shapes, entrypoints
```

## Clean gate — NOT run directly against this fixture's own path

The clean gate deliberately excludes any path containing a `negative_`-prefixed component
(`oe_method_clean_gate_v1_4_0.py` onward), so that a real compliance scan of the whole package
doesn't false-fail on its own shipped negative fixtures. Running it directly against this
fixture's own path therefore reports `0 text files scanned` — correctly, by the same exclusion
that protects a real release. To actually observe the failure this fixture demonstrates, copy
`plant.md` to a path with no `negative_`-prefixed component and run the gate there:

```
clean gate: 1 text files scanned, 1 matches
   [person] plant.md line 2: Yusuf
VERDICT: FAIL — personal or project data present
```

This is the same real mechanism the original, separate `negative_clean_planted_name_v1_0_0`
fixture relied on — copy-out-and-test, not run-in-place — made explicit here rather than left
implicit.
