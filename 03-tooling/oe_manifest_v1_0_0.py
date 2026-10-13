#!/usr/bin/env python3
"""oe_manifest_v1_0_0 - write the manifest of a package stage, and prove it verifies (plan v1.16.0, owner 2026-10-07: shorter runs).

Every session wrote its own script for this and every one tripped on the same things: bytecode a test run left behind (a stowaway), the old manifest still
listed, a record the publisher regenerates. This tool does the whole step and refuses to report success unless the result verifies in BOTH directions
(every listed file matches, no file is unlisted), with the same rule the publisher applies.

  python3 oe_manifest_v1_0_0.py <stage> [--name MANIFEST_SHA256.txt] [--note "<one line>"]

What it does, in this order:
  1. removes __pycache__ folders and *.pyc files anywhere in the stage, and PUBLISH_RECORD.ttl at its root (the publisher writes that one); says how many
  2. removes the stage's earlier manifest(s) at the root; the new one keeps the form the stage already had (MANIFEST_SHA256.txt, or MANIFEST_SHA256_v<version>.txt
     built from VERSION.txt when the earlier one was versioned) unless --name is given
  3. writes the manifest: sha256 and size of every file, sorted, the manifest itself and PUBLISH_RECORD.ttl excluded
  4. re-reads the file it wrote and verifies it both ways; exit 0 only if it verifies

Exit codes: 0 written and verified; 1 verification failed; 2 usage or a stage without VERSION.txt."""
import hashlib, os, re, shutil, sys

ROOT_MANIFEST = re.compile(r"^MANIFEST_SHA256.*\.txt$")


def clean(stage):
    n = 0
    for r, ds, fs in os.walk(stage):
        for d in [d for d in ds if d == "__pycache__"]:
            shutil.rmtree(os.path.join(r, d)); n += 1
        ds[:] = [d for d in ds if d != "__pycache__" and d != ".git"]
        for f in fs:
            if f.endswith(".pyc"):
                os.remove(os.path.join(r, f)); n += 1
    rec = os.path.join(stage, "PUBLISH_RECORD.ttl")
    if os.path.isfile(rec):
        os.remove(rec); n += 1
    return n


def pick_name(stage, explicit):
    if explicit:
        return explicit
    old = sorted(f for f in os.listdir(stage) if ROOT_MANIFEST.match(f) and os.path.isfile(os.path.join(stage, f)))
    if old and "_v" in old[-1]:
        ver = open(os.path.join(stage, "VERSION.txt"), encoding="utf-8").read().strip().replace(".", "_")
        return "MANIFEST_SHA256_v%s.txt" % ver
    return "MANIFEST_SHA256.txt"


def files_of(stage, skip):
    out = []
    for r, ds, fs in os.walk(stage):
        ds[:] = sorted(d for d in ds if d != ".git")
        for f in fs:
            rel = os.path.relpath(os.path.join(r, f), stage).replace(os.sep, "/")
            if rel in skip or os.path.basename(rel) == "PUBLISH_RECORD.ttl":
                continue
            out.append(rel)
    return sorted(out)


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for ch in iter(lambda: fh.read(1 << 20), b""):
            h.update(ch)
    return h.hexdigest()


def write(stage, name, note):
    rows = []
    for rel in files_of(stage, {name}):
        p = os.path.join(stage, rel)
        rows.append((rel, sha(p), os.path.getsize(p)))
    with open(os.path.join(stage, name), "w", encoding="utf-8") as fh:
        fh.write(note.rstrip() + "\n\n" + "".join("%s  %s  (%db)\n" % (h, rel, n) for rel, h, n in rows))
    return len(rows)


def verify(stage, name):
    """both directions, the publisher's rule: every listed file matches; no file on disk is unlisted"""
    listed = {}
    for ln in open(os.path.join(stage, name), encoding="utf-8"):
        m = re.match(r"^([0-9a-fA-F]{64})\s+[*]?(\S.*?)(?:\s+\(\d+b\))?$", ln.strip())
        if m:
            listed[m.group(2)] = m.group(1)
    bad = [rel for rel, h in listed.items() if not os.path.isfile(os.path.join(stage, rel)) or sha(os.path.join(stage, rel)) != h]
    stowaways = [rel for rel in files_of(stage, {name}) if rel not in listed]
    return len(listed), bad, stowaways


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 2
    stage = os.path.abspath(argv[0]); name = None; note = None
    i = 1
    while i < len(argv):
        if argv[i] == "--name" and i + 1 < len(argv): name = argv[i + 1]; i += 2
        elif argv[i] == "--note" and i + 1 < len(argv): note = argv[i + 1]; i += 2
        else: print("REFUSED: unknown argument " + argv[i], file=sys.stderr); return 2
    if not os.path.isdir(stage) or not os.path.isfile(os.path.join(stage, "VERSION.txt")):
        print("REFUSED: %s is not a package stage (no VERSION.txt)" % stage, file=sys.stderr); return 2
    removed = clean(stage)
    name = pick_name(stage, name)
    for f in os.listdir(stage):
        if ROOT_MANIFEST.match(f) and os.path.isfile(os.path.join(stage, f)):
            os.remove(os.path.join(stage, f))
    ver = open(os.path.join(stage, "VERSION.txt"), encoding="utf-8").read().strip()
    n = write(stage, name, note or ("%s v%s: manifest" % (os.path.basename(stage.rstrip("/")), ver)))
    total, bad, stow = verify(stage, name)
    print("manifest %s: %d file(s) listed, %d bytecode/record file(s) removed" % (name, n, removed))
    if bad or stow or total != n:
        print("FAIL: mismatched %s; unlisted %s" % (bad[:5], stow[:5]), file=sys.stderr); return 1
    print("verified both ways: every listed file matches, none unlisted")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
