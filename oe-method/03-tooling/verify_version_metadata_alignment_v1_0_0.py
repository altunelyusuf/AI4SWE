#!/usr/bin/env python3
"""verify_version_metadata_alignment_v1_0_0.py

Proposal P1 candidate for OE Pack release_check pipeline.
Author: a domain ecosystem session, 2026-05-29.
License: CC BY 4.0.

Per-file verification that an ontology's three loci of version truth agree:
  1. The filename SemVer suffix (per BP-D6 / OntologyFileConvention,
     TBoxFileConvention, ABoxFileConvention, ShapeFileConvention).
  2. The owl:versionInfo string literal inside the file.
  3. The SemVer suffix of the owl:versionIRI URI inside the file.

Each file is parsed in isolation. This is intentional: merging TBox + ABox
into a single graph (as pyshacl does) collapses both files' ontology
declarations onto the same IRI and produces a cross-product that causes
false-positive misalignment readings. The per-file approach avoids this.

Usage:
    python3 verify_version_metadata_alignment_v1_0_0.py <directory>

Exit code 0 if all aligned; exit code 1 if any mismatch.

What this script does NOT do (out of scope by design):
  - Validate that owl:versionInfo or owl:versionIRI exist
    (OntologyHeaderShape already covers that).
  - Validate SHACL or HermiT (separate gates).
  - Check non-SemVer version strings (recorded as a skip with note).
"""

import os
import re
import sys
import glob
from typing import List, Optional, Tuple

try:
    import rdflib
    from rdflib import OWL, RDF
except ImportError:
    print("FAIL: rdflib not installed", file=sys.stderr)
    sys.exit(2)

# Filename pattern from BP-D6: ^[a-z][a-z0-9_]*_v(\d+)_(\d+)_(\d+)\.ttl$
# (relaxed slightly to also accept TBoxFileConvention / ABoxFileConvention etc.,
#  which all share the _v{M}_{m}_{p} tail)
FILENAME_VERSION_RE = re.compile(r"_v(\d+)_(\d+)_(\d+)\.ttl$")

# SemVer suffix of a versionIRI: trailing /<major>.<minor>.<patch>
IRI_VERSION_RE = re.compile(r"/(\d+\.\d+\.\d+)$")


def extract_filename_version(path: str) -> Optional[str]:
    """Return the SemVer string from a filename, or None if not SemVer-named."""
    m = FILENAME_VERSION_RE.search(os.path.basename(path))
    if not m:
        return None
    return f"{m.group(1)}.{m.group(2)}.{m.group(3)}"


def check_file(path: str) -> Tuple[str, str, dict]:
    """
    Return (status, message, detail) where status is one of:
      'OK', 'MISMATCH', 'NON_SEMVER_SKIP', 'NO_ONTOLOGY_DECL',
      'MULTIPLE_ONTOLOGY_DECL', 'PARSE_ERROR'.
    """
    detail = {"file": path}

    try:
        g = rdflib.Graph()
        g.parse(path)
    except Exception as e:
        return ("PARSE_ERROR", f"rdflib parse failed: {e}", detail)

    onts = list(g.subjects(RDF.type, OWL.Ontology))
    if len(onts) == 0:
        return ("NO_ONTOLOGY_DECL", "no owl:Ontology declaration found", detail)
    if len(onts) > 1:
        detail["ontology_iris"] = [str(o) for o in onts]
        return ("MULTIPLE_ONTOLOGY_DECL",
                f"{len(onts)} owl:Ontology declarations in one file (unusual; investigate)",
                detail)

    ont = onts[0]
    detail["ontology_iri"] = str(ont)

    info = g.value(ont, OWL.versionInfo)
    iri = g.value(ont, OWL.versionIRI)
    fn_version = extract_filename_version(path)

    detail["versionInfo"] = str(info) if info else None
    detail["versionIRI"] = str(iri) if iri else None
    detail["filename_version"] = fn_version

    # All three loci — collect the SemVer strings where available.
    semvers = {}
    if fn_version:
        semvers["filename"] = fn_version
    if info:
        info_str = str(info)
        # Only treat as SemVer-comparable if it matches the pattern.
        if re.match(r"^\d+\.\d+\.\d+$", info_str):
            semvers["versionInfo"] = info_str
        else:
            # Non-SemVer versionInfo — skip with note.
            return ("NON_SEMVER_SKIP",
                    f"versionInfo='{info_str}' is not SemVer; skipping",
                    detail)
    if iri:
        m = IRI_VERSION_RE.search(str(iri))
        if m:
            semvers["versionIRI"] = m.group(1)

    if len(semvers) < 2:
        # Fewer than two loci have SemVer strings; nothing to compare.
        # OntologyHeaderShape covers the absence case.
        return ("OK",
                f"only {len(semvers)} SemVer locus present; out of this gate's scope",
                detail)

    # Compare. All present SemVer values must agree.
    unique = set(semvers.values())
    if len(unique) == 1:
        return ("OK", f"all loci agree at {unique.pop()}", detail)

    detail["semvers"] = semvers
    msg = "MISMATCH: " + " vs ".join(f"{k}={v}" for k, v in sorted(semvers.items()))
    return ("MISMATCH", msg, detail)


def main(argv: List[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0

    target = argv[1]
    if os.path.isdir(target):
        files = sorted(glob.glob(os.path.join(target, "*.ttl")))
    elif os.path.isfile(target):
        files = [target]
    else:
        print(f"FAIL: not a file or directory: {target}", file=sys.stderr)
        return 2

    if not files:
        print(f"no .ttl files found in {target}", file=sys.stderr)
        return 0

    n_ok = n_mismatch = n_skip = n_other = 0
    mismatches = []
    others = []

    for f in files:
        status, msg, detail = check_file(f)
        if status == "OK":
            n_ok += 1
        elif status == "MISMATCH":
            n_mismatch += 1
            mismatches.append((f, msg, detail))
        elif status == "NON_SEMVER_SKIP":
            n_skip += 1
        else:
            n_other += 1
            others.append((f, status, msg, detail))

    print(f"--- VersionMetadataAlignment gate ---")
    print(f"  scanned: {len(files)} file(s)")
    print(f"  OK:                {n_ok}")
    print(f"  MISMATCH:          {n_mismatch}")
    print(f"  NON_SEMVER_SKIP:   {n_skip}")
    print(f"  OTHER (parse/decl): {n_other}")

    if mismatches:
        print(f"\n--- MISMATCHES ({len(mismatches)}) ---")
        for f, msg, detail in mismatches:
            print(f"  FAIL {os.path.basename(f)}")
            print(f"    {msg}")
            print(f"    ontology IRI: {detail.get('ontology_iri')}")
            print(f"    versionInfo:  {detail.get('versionInfo')}")
            print(f"    versionIRI:   {detail.get('versionIRI')}")
            print(f"    filename ver: {detail.get('filename_version')}")

    if others:
        print(f"\n--- OTHER ({len(others)}) ---")
        for f, status, msg, _ in others:
            print(f"  {status} {os.path.basename(f)}: {msg}")

    return 1 if n_mismatch > 0 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
