#!/usr/bin/env python3
"""
validate_with_imports_v1_1_0.py — OE Pack SHACL validation helper with optional
SHA-keyed cache integration.

Lineage: CONTINUATION of validate_with_imports.py v1.0.0 (which remains in
this directory unchanged for audit-trail integrity). v1.1.0 adds an optional
--cache-dir argument that routes the validation result through the shacl_cache
wrapper module (Track D from v17.11.0). Default behaviour is byte-identical
to v1.0.0 when no cache is configured.

Closes Issue I-09 (Phase 1) by formalizing the standalone-vs-imports-merged
validation pattern that has been re-discovered across Sprints 7, 8, meta-sprint,
and the v1.0.x review work.

CACHE INTEGRATION (v17.13.0, Track D wiring)

When --cache-dir DIR is provided (or OEPACK_USE_SHACL_CACHE env var is set to
a non-empty value, which defaults --cache-dir to /tmp/oepack_shacl_cache),
this module:

  1. Computes a stable cache key from the file-fingerprints of:
        - data_paths
        - shapes_paths
        - file-fingerprints of files in imports_lookup_dirs
        - all validation options (inference, advanced, strip_imports_*,
          iri_to_path_overrides) serialized as canonical JSON
  2. On HIT: deserializes the cached (conforms, results_graph_nt, results_text,
     summary), returns without invoking pyshacl OR resolve_imports.
  3. On MISS: runs the full v1.0.0 path (resolve_imports + pyshacl + summary),
     then stores the result before returning.

Empirical evidence for cache effectiveness was established in v17.11.0 Track D
gate test (8,891× speedup on slow C7+ shape via shacl_cache_v1_0_0).

HONEST DISCLOSURE

Cache key MISSES on these cases (same trade-off as standalone Track D):
  - Any source file's bytes change (intended)
  - A user reorders triples within a file (false miss; safe — re-runs pyshacl)
  - A user renames a BNode locally in a file (false miss; safe)
  - Imports lookup dirs add/remove files (intended — different effective inputs)

The cache CANNOT produce false HITS because any input change updates the key.

Usage (programmatic):

    from validate_with_imports_v1_1_0 import validate_with_imports
    conforms, results_g, results_text, summary = validate_with_imports(
        data_paths=["/path/to/my_artifact.ttl"],
        shapes_paths=["/path/to/v17/shapes/redo_shacl.ttl", ...],
        imports_lookup_dirs=["/path/to/v16/base/", "/path/to/sprint_outputs/"],
        inference="rdfs",
        advanced=True,
        cache_dir="/tmp/oepack_shacl_cache",  # NEW in v1.1.0
    )

Usage (programmatic):

    from validate_with_imports import validate_with_imports
    conforms, results_g, results_text, summary = validate_with_imports(
        data_paths=["/path/to/my_artifact.ttl"],
        shapes_paths=["/path/to/v17/shapes/redo_shacl.ttl", ...],
        imports_lookup_dirs=["/path/to/v16/base/", "/path/to/sprint_outputs/"],
        inference="rdfs",
        advanced=True,
    )

Usage (CLI):

    python3 validate_with_imports_v1_1_0.py \\
        --data my_artifact.ttl \\
        --shapes v17/shapes/redo_shacl.ttl v17/shapes/oqc_shacl.ttl \\
        --imports-dir v16/base/ \\
        --imports-dir sprint_outputs/ \\
        --inference rdfs --advanced \\
        --cache-dir /tmp/oepack_shacl_cache \\
        --report-out validation_report.txt

Exit codes:
    0 — all conform (V=0 W=0)
    1 — violations present
    2 — warnings present (no violations)
    3 — usage / file error

This is the canonical implementation of Best Practice BP-1
(Standalone-vs-imports-merged validation pattern).

Author: Phase 1 Structural Cleanup, I-09 remediation
Version: 1.1.0
Date: 2026-05-12 (v17.13.0 Track D wiring)
Discipline: per catalogue v1.0.7.7 (Track D auto-routing into validate_with_imports)
License: Same as OE Pack
"""
import argparse
import os
import sys
from typing import Iterable, Optional

from rdflib import Graph, URIRef
from rdflib.namespace import OWL


# ─────────────────────────────────────────────────────────────────────────────
# Core helper
# ─────────────────────────────────────────────────────────────────────────────

# OE Pack default IRI → file-basename-fragment mapping. The META ontology IRI is
# `http://example.org/ontology-engineering` but its file is named `meta_v*.ttl`,
# so basename matching alone misses it. Users can add their own overrides.
DEFAULT_OE_PACK_IRI_HINTS: dict[str, list[str]] = {
    "http://example.org/ontology-engineering": ["meta_"],
    "http://example.org/reliability":           ["redo_"],
    "http://example.org/quality":               ["oqc_"],
    "http://example.org/amod":                  ["amod_"],
    "http://example.org/core":                  ["core_"],
    "http://example.org/oqc-measurements":      ["oqc_measurements"],
    "http://example.org/oem-bridge":            ["oem_bridge"],
    "http://example.org/oee-alignment":         ["oee_alignment"],
}


def resolve_imports(
    initial_paths: Iterable[str],
    lookup_dirs: Iterable[str],
    *,
    iri_to_path_overrides: Optional[dict[str, str]] = None,
    iri_basename_hints: Optional[dict[str, list[str]]] = None,
    max_depth: int = 8,
    strip_imports: bool = True,
    verbose: bool = False,
) -> Graph:
    """Load files in initial_paths into a graph; recursively follow owl:imports
    by mapping import IRIs to local files in lookup_dirs.

    Lookup strategy (in order):
        1. iri_to_path_overrides[iri] — explicit mapping wins.
        2. iri_basename_hints[iri] — list of basename fragments to match.
        3. DEFAULT_OE_PACK_IRI_HINTS — built-in OE Pack mapping (covers META,
           a reliability ontology, OQC, AMOD, CORE, etc.).
        4. Tail-of-IRI substring match — for generic IRIs (e.g.,
           http://example.org/foo → matches *foo*.ttl).

    Args:
        initial_paths: TTL file paths to seed the graph.
        lookup_dirs: directories to search for imported ontologies.
        iri_to_path_overrides: explicit IRI → absolute-path mapping; wins over
            all other strategies.
        iri_basename_hints: IRI → list of basename fragments (any-of match).
            Merged on top of DEFAULT_OE_PACK_IRI_HINTS.
        max_depth: maximum import-resolution recursion depth.
        verbose: if True, print resolution traces to stderr.

    Returns:
        A merged rdflib.Graph containing the union of the seed graphs and all
        successfully resolved imports. owl:imports triples are stripped from
        the merged graph (HermiT-friendly).
    """
    g = Graph()
    seen_iris: set[str] = set()
    seen_paths: set[str] = set()

    overrides = dict(iri_to_path_overrides or {})
    hints = dict(DEFAULT_OE_PACK_IRI_HINTS)
    if iri_basename_hints:
        for k, v in iri_basename_hints.items():
            hints.setdefault(k, []).extend(v)

    # Build a basename → full-path index of the lookup directories
    file_index: dict[str, str] = {}
    for d in lookup_dirs:
        if not os.path.isdir(d):
            if verbose:
                print(f"[validate_with_imports] WARNING: lookup dir not found: {d}", file=sys.stderr)
            continue
        for entry in os.listdir(d):
            if entry.endswith(".ttl"):
                file_index[entry] = os.path.join(d, entry)

    def _try_load_iri(iri: str, depth: int) -> bool:
        if iri in seen_iris or depth > max_depth:
            return False
        seen_iris.add(iri)

        # Strategy 1: explicit override
        if iri in overrides:
            chosen = overrides[iri]
            if not os.path.isfile(chosen):
                print(f"[validate_with_imports] override path not found: {chosen}", file=sys.stderr)
                return False
            return _load_path(chosen, depth, iri)

        candidates: list[str] = []

        # Strategy 2/3: basename hints
        for hint_iri, fragments in hints.items():
            if iri == hint_iri:
                for fname, fpath in file_index.items():
                    if any(frag in fname for frag in fragments):
                        candidates.append(fpath)
                if candidates:
                    break

        # Strategy 4: tail-of-IRI substring
        if not candidates:
            tail = iri.rstrip("/").rsplit("/", 1)[-1].rsplit("#", 1)[-1]
            for fname, fpath in file_index.items():
                base = os.path.splitext(fname)[0]
                if tail and (tail in base or base.startswith(tail)):
                    candidates.append(fpath)
            for fname, fpath in file_index.items():
                if fname == f"{tail}.ttl" and fpath not in candidates:
                    candidates.append(fpath)

        if not candidates:
            if verbose:
                print(f"[validate_with_imports] {iri}: no local file found", file=sys.stderr)
            return False
        chosen = sorted(candidates)[-1]  # most recent / lexicographic last
        return _load_path(chosen, depth, iri)

    def _load_path(chosen: str, depth: int, iri_for_log: str) -> bool:
        if chosen in seen_paths:
            return True
        seen_paths.add(chosen)
        if verbose:
            print(f"[validate_with_imports] {iri_for_log} → {chosen}", file=sys.stderr)
        sub_g = Graph()
        try:
            sub_g.parse(chosen, format="turtle")
        except Exception as e:
            print(f"[validate_with_imports] ERROR parsing {chosen}: {e}", file=sys.stderr)
            return False
        for t in sub_g:
            g.add(t)
        for imp in sub_g.objects(predicate=OWL.imports):
            _try_load_iri(str(imp), depth + 1)
        return True

    # Seed: load initial files
    for path in initial_paths:
        if not os.path.isfile(path):
            print(f"[validate_with_imports] ERROR: file not found: {path}", file=sys.stderr)
            continue
        if path in seen_paths:
            continue
        seen_paths.add(path)
        if verbose:
            print(f"[validate_with_imports] seed: {path}", file=sys.stderr)
        sub_g = Graph()
        sub_g.parse(path, format="turtle")
        for t in sub_g:
            g.add(t)
        for imp in sub_g.objects(predicate=OWL.imports):
            _try_load_iri(str(imp), 1)

    # Optionally strip owl:imports from the merged graph. Default True for
    # HermiT-friendliness (HermiT will try to network-resolve unknown imports).
    # Set False when the SHACL shapes need to read owl:imports declarations
    # from the data graph (e.g., a reliability ontology C7+ TypeDeclarationShape post-I-05).
    if strip_imports:
        for s, p, o in list(g.triples((None, OWL.imports, None))):
            g.remove((s, p, o))

    return g


def validate_with_imports(
    data_paths: Iterable[str],
    shapes_paths: Iterable[str],
    imports_lookup_dirs: Iterable[str] = (),
    *,
    inference: str = "rdfs",
    advanced: bool = True,
    iri_to_path_overrides: Optional[dict[str, str]] = None,
    iri_basename_hints: Optional[dict[str, list[str]]] = None,
    strip_imports_data: bool = False,
    strip_imports_shapes: bool = True,
    verbose: bool = False,
    cache_dir: Optional[str] = None,  # NEW v1.1.0: Track D cache integration
) -> tuple[bool, Graph, str, dict]:
    """Run pyshacl validation with automatic owl:imports resolution.

    Args:
        data_paths: list of TTL files containing the data graph.
        shapes_paths: list of TTL files containing SHACL shapes.
        imports_lookup_dirs: list of directories to search for imported
            ontologies. For OE Pack, typically the v16 base directory.
        inference: pyshacl inference setting (default "rdfs").
        advanced: enable SHACL Advanced Features (default True).
        iri_to_path_overrides: explicit IRI → file-path mapping.
        iri_basename_hints: IRI → basename-fragment hints.
        strip_imports_data: strip owl:imports from the data graph after merge.
            Default False because some shapes (e.g., a reliability ontology C7+ post-I-05)
            inspect owl:imports declarations on the focus graph to decide what
            counts as a "known" type vocabulary.
        strip_imports_shapes: strip owl:imports from the shapes graph after merge.
            Default True (shapes graphs don't need owl:imports for HermiT).
        verbose: print resolution traces to stderr.

    Returns:
        (conforms, results_graph, results_text, summary)
    """
    try:
        from pyshacl import validate
    except ImportError as e:
        raise ImportError("pyshacl is required: pip install pyshacl") from e

    # NEW v1.1.0: cache lookup (BEFORE expensive resolve_imports + pyshacl)
    # If cache_dir set, attempt to serve from cache. If MISS, fall through to
    # the v1.0.0 path and store the result before returning.
    if cache_dir is not None:
        try:
            # Import lazily so v1.1.0 still works if shacl_cache is absent
            # (in which case cache is silently disabled with a stderr warning).
            import sys as _sys
            import os as _os
            _tools_dir = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                       "..", "13-phase29-deliverables", "tools")
            _tools_dir = _os.path.normpath(_tools_dir)
            if _tools_dir not in _sys.path:
                _sys.path.insert(0, _tools_dir)
            from shacl_cache_v1_0_0 import (
                _file_sha256 as _vw_file_sha256,
                _fileset_fingerprint as _vw_fileset_fp,
            )
        except ImportError as _imp_err:
            print(f"validate_with_imports_v1_1_0: cache requested but "
                  f"shacl_cache_v1_0_0 not importable ({_imp_err}); "
                  f"continuing without cache.", file=sys.stderr)
            cache_dir = None

    if cache_dir is not None:
        import hashlib, json
        os.makedirs(cache_dir, exist_ok=True)

        # Collect file paths for imports_lookup_dirs (a SET of .ttl files
        # in those dirs; not the dirs themselves, since dir names alone
        # would miss content changes inside).
        imports_files = []
        for _d in (imports_lookup_dirs or ()):
            if os.path.isdir(_d):
                for _root, _, _files in os.walk(_d):
                    for _fn in _files:
                        if _fn.endswith(".ttl"):
                            imports_files.append(os.path.join(_root, _fn))
        imports_files = sorted(set(imports_files))

        opts = {
            "inference": inference,
            "advanced": advanced,
            "iri_to_path_overrides": iri_to_path_overrides or {},
            "iri_basename_hints": iri_basename_hints or {},
            "strip_imports_data": strip_imports_data,
            "strip_imports_shapes": strip_imports_shapes,
        }
        try:
            d_fp = _vw_fileset_fp(list(data_paths))
            s_fp = _vw_fileset_fp(list(shapes_paths))
            i_fp = _vw_fileset_fp(imports_files) if imports_files else "no-imports"
        except Exception as _fp_err:
            print(f"validate_with_imports_v1_1_0: fingerprint computation "
                  f"failed ({_fp_err}); continuing without cache.",
                  file=sys.stderr)
            cache_dir = None

    if cache_dir is not None:
        opts_blob = json.dumps(opts, sort_keys=True).encode("utf-8")
        key = hashlib.sha256((d_fp + s_fp + i_fp).encode("utf-8") + opts_blob).hexdigest()
        cache_path = os.path.join(cache_dir, f"vwi_{key}.json")

        if os.path.exists(cache_path):
            try:
                with open(cache_path) as _f:
                    _entry = json.load(_f)
                if verbose:
                    print(f"[validate_with_imports v1.1.0] CACHE HIT key={key[:24]}...",
                          file=sys.stderr)
                results_g = Graph()
                if _entry.get("results_graph_nt"):
                    results_g.parse(data=_entry["results_graph_nt"], format="nt")
                return (_entry["conforms"], results_g,
                        _entry["results_text"], _entry["summary"])
            except Exception as _cache_err:
                print(f"validate_with_imports_v1_1_0: cache read failed "
                      f"({_cache_err}); falling through to fresh run.",
                      file=sys.stderr)

        if verbose:
            print(f"[validate_with_imports v1.1.0] CACHE MISS key={key[:24]}...",
                  file=sys.stderr)

    data_g = resolve_imports(
        data_paths, imports_lookup_dirs,
        iri_to_path_overrides=iri_to_path_overrides,
        iri_basename_hints=iri_basename_hints,
        strip_imports=strip_imports_data,
        verbose=verbose,
    )
    shapes_g = resolve_imports(
        shapes_paths, imports_lookup_dirs,
        iri_to_path_overrides=iri_to_path_overrides,
        iri_basename_hints=iri_basename_hints,
        strip_imports=strip_imports_shapes,
        verbose=verbose,
    )

    if verbose:
        print(f"[validate_with_imports] data graph: {len(data_g):,} triples", file=sys.stderr)
        print(f"[validate_with_imports] shapes graph: {len(shapes_g):,} triples", file=sys.stderr)

    conforms, results_g, results_text = validate(
        data_graph=data_g,
        shacl_graph=shapes_g,
        inference=inference,
        advanced=advanced,
    )

    # Summarize severity counts via SPARQL
    summary = {
        "violations": 0,
        "warnings": 0,
        "infos": 0,
        "data_triples": len(data_g),
        "shapes_triples": len(shapes_g),
    }
    if not conforms:
        sql = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        SELECT ?sev (COUNT(?r) AS ?n)
        WHERE { ?r a sh:ValidationResult ; sh:resultSeverity ?sev }
        GROUP BY ?sev
        """
        for row in results_g.query(sql):
            sev_str = str(row[0]).split("#")[-1] if row[0] else "?"
            n = int(row[1])
            if sev_str == "Violation":
                summary["violations"] = n
            elif sev_str == "Warning":
                summary["warnings"] = n
            elif sev_str == "Info":
                summary["infos"] = n

    # NEW v1.1.0: store to cache on MISS path (cache_dir is set and we got here)
    if cache_dir is not None:
        try:
            _entry_out = {
                "conforms": bool(conforms),
                "results_graph_nt": results_g.serialize(format="nt") if results_g else None,
                "results_text": results_text or "",
                "summary": summary,
                "cache_key": key,
            }
            with open(cache_path, "w") as _f:
                json.dump(_entry_out, _f)
            if verbose:
                print(f"[validate_with_imports v1.1.0] CACHE STORED key={key[:24]}...",
                      file=sys.stderr)
        except Exception as _cache_err:
            print(f"validate_with_imports_v1_1_0: cache write failed "
                  f"({_cache_err}); result returned but not cached.",
                  file=sys.stderr)

    return conforms, results_g, results_text, summary


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main(argv: Optional[list[str]] = None) -> int:
    p = argparse.ArgumentParser(
        description="OE Pack SHACL validation with automatic owl:imports resolution.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--data", nargs="+", required=True,
                   help="Data graph TTL file(s).")
    p.add_argument("--shapes", nargs="+", required=True,
                   help="SHACL shape graph TTL file(s).")
    p.add_argument("--imports-dir", action="append", default=[], dest="imports_dirs",
                   help="Directory to search for imported ontologies (repeatable).")
    p.add_argument("--inference", default="rdfs",
                   choices=("none", "rdfs", "owlrl", "both"),
                   help="pyshacl inference setting (default: rdfs)")
    p.add_argument("--advanced", action="store_true", default=True,
                   help="Enable SHACL Advanced Features (default: True)")
    p.add_argument("--no-advanced", action="store_false", dest="advanced",
                   help="Disable SHACL Advanced Features")
    p.add_argument("--report-out", default=None,
                   help="Write validation report text to this file.")
    p.add_argument("--cache-dir", default=None,
                   help="Optional cache directory (Track D, v17.13.0). "
                        "If unset, OEPACK_USE_SHACL_CACHE env var enables "
                        "cache with default dir /tmp/oepack_shacl_cache.")
    p.add_argument("-v", "--verbose", action="store_true",
                   help="Print imports-resolution traces and cache "
                        "HIT/MISS to stderr.")
    args = p.parse_args(argv)

    # Validate inputs exist
    for path in list(args.data) + list(args.shapes):
        if not os.path.isfile(path):
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 3
    for d in args.imports_dirs:
        if not os.path.isdir(d):
            print(f"WARNING: imports directory not found: {d}", file=sys.stderr)

    # NEW v1.1.0: resolve cache_dir from --cache-dir or env var
    _cache_dir = args.cache_dir
    if _cache_dir is None and os.environ.get("OEPACK_USE_SHACL_CACHE"):
        _cache_dir = "/tmp/oepack_shacl_cache"

    try:
        conforms, results_g, results_text, summary = validate_with_imports(
            data_paths=args.data,
            shapes_paths=args.shapes,
            imports_lookup_dirs=args.imports_dirs,
            inference=args.inference,
            advanced=args.advanced,
            verbose=args.verbose,
            cache_dir=_cache_dir,
        )
    except Exception as e:
        print(f"ERROR: validation failed: {e}", file=sys.stderr)
        return 3

    print(f"Conforms: {conforms}")
    print(f"Data triples (with imports merged): {summary['data_triples']:,}")
    print(f"Shapes triples (with imports merged): {summary['shapes_triples']:,}")
    print(f"Violations: {summary['violations']}")
    print(f"Warnings:   {summary['warnings']}")
    print(f"Infos:      {summary['infos']}")

    if args.report_out:
        with open(args.report_out, "w") as f:
            f.write(results_text)
        print(f"Full report written to: {args.report_out}")

    if summary["violations"] > 0:
        return 1
    if summary["warnings"] > 0:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
