#!/usr/bin/env python3
"""oe_resolve_v1_0_0 - find a governing artifact of a package in either layout (OEE consolidation, P3).

A package ships its knowledge base either as its own file (01-vocabularies|01-ontologies/knowledge_base_abox_v*.ttl) or, after the consolidation (BP-D54),
as a MODULE inside the A-Box of its governance unit (a file *_abox_v*.ttl that holds the knowledge-base vocabulary: kb:hasLessonId or kb:hasBestPracticeId).
This tool prints the path of the highest-SemVer file that holds it, so a session never has to remember a file name (BP-D6).

Usage: oe_resolve_v1_0_0.py <package-dir> kb        prints the path; exit 0, or exit 2 and a message on stderr when nothing is found
A found file is a real knowledge base only when it has lessons or best practices: an empty hit is not a result.
"""
import glob, os, re, sys

MARK = (b"hasLessonId", b"hasBestPracticeId")


def vkey(p):
    return [int(x) for x in re.findall(r"\d+", os.path.basename(p))[-3:]]


def holds_kb(path):
    try:
        b = open(path, "rb").read()
    except OSError:
        return False
    return any(m in b for m in MARK)


def resolve_kb(pkg):
    old = sorted(glob.glob(os.path.join(pkg, "01-vocabularies", "knowledge_base_abox_v*.ttl")) + glob.glob(os.path.join(pkg, "01-ontologies", "knowledge_base_abox_v*.ttl")), key=vkey)
    if old and holds_kb(old[-1]):
        return old[-1]
    cands = []
    for r, ds, fs in os.walk(pkg):
        ds[:] = [d for d in ds if d not in (".git", "__pycache__", "fixtures", "archive") and not d.startswith("vendored")]
        for f in fs:
            if re.search(r"_abox_v\d+_\d+_\d+\.ttl$", f):
                cands.append(os.path.join(r, f))
    hits = sorted((c for c in cands if holds_kb(c)), key=vkey)
    return hits[-1] if hits else None


def main(argv):
    if len(argv) != 2 or argv[1] != "kb":
        print(__doc__); return 2
    p = resolve_kb(argv[0])
    if not p:
        print(f"REFUSED: no knowledge base found under {argv[0]} (neither a knowledge_base_abox file nor an A-Box that holds it)", file=sys.stderr); return 2
    print(p); return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
