#!/usr/bin/env python3
"""oe_gate_receipt_v1_0_0 - a package's own gates ran on THESE bytes and passed; do not run them again on the same bytes (plan v1.17.0).

The publisher runs a package's gates in the dry-run and again in the real publish. For a package whose gate takes minutes that is the whole of the release.
The second run learns nothing the first did not, if everything the gate reads is the same. This tool records what the gate read and says whether it is still the same:

  oe_gate_receipt_v1_0_0.py write <stage> --origin <sha> [--extra DIR ...] [--seconds N]
  oe_gate_receipt_v1_0_0.py check <stage> --origin <sha> [--extra DIR ...] [--max-age SECONDS]      exit 0 valid, 1 not valid (the reason is printed)

A receipt is valid only if ALL of these are unchanged since it was written: the digest of every file in the stage (the gates are in the stage, so a changed gate
invalidates it; bytecode and PUBLISH_RECORD.ttl are left out), the digest of each --extra tree (what the gate reads outside the stage, such as the sibling
package a lineage gate compares with), the head commit of the target repository (--origin: a gate that reads a neighbour can change its verdict when the
neighbour moves), the Python version, and its age is at most --max-age (default 3600 s). The receipt is kept beside the stage, never inside it
(<stage>.oe_gate_receipt.json). Only a pass is ever written. A gate that reads something this tool is not told about (the network, the clock, a database)
is not covered; such a gate must not be reused and the publisher is told so with OE_FRESH_GATES=1.

Exit codes: 0 done / valid; 1 not valid; 2 usage."""
import hashlib, json, os, sys, time


def tree_digest(root):
    rows = []
    for r, ds, fs in os.walk(root):
        ds[:] = sorted(d for d in ds if d not in (".git", "__pycache__"))
        for f in fs:
            if f.endswith(".pyc") or (f == "PUBLISH_RECORD.ttl" and os.path.normpath(r) == os.path.normpath(root)):
                continue
            p = os.path.join(r, f); h = hashlib.sha256()
            with open(p, "rb") as fh:
                for ch in iter(lambda: fh.read(1 << 20), b""): h.update(ch)
            rows.append("%s\t%s" % (os.path.relpath(p, root).replace(os.sep, "/"), h.hexdigest()))
    return hashlib.sha256("\n".join(sorted(rows)).encode()).hexdigest(), len(rows)


def path_of(stage): return stage.rstrip("/") + ".oe_gate_receipt.json"


def state(stage, origin, extras):
    sd, n = tree_digest(stage)
    return {"stage": sd, "files": n, "origin": origin or "", "extras": {os.path.abspath(e): tree_digest(e)[0] for e in extras}, "python": sys.version.split()[0]}


def write(stage, origin, extras, seconds):
    r = state(stage, origin, extras); r["written"] = time.time(); r["gate_seconds"] = seconds
    json.dump(r, open(path_of(stage), "w"))
    return r


def check(stage, origin, extras, max_age=3600):
    try: old = json.load(open(path_of(stage)))
    except Exception: return False, "no receipt"
    cur = state(stage, origin, extras)
    for k in ("stage", "origin", "extras", "python"):
        if old.get(k) != cur[k]:
            return False, "%s changed since the receipt" % k
    age = time.time() - old.get("written", 0)
    if age > max_age: return False, "receipt is %d s old (limit %d)" % (age, max_age)
    return True, "gates passed %d s ago on these exact bytes (took %s s)" % (age, old.get("gate_seconds", "?"))


def main(argv):
    if len(argv) < 2 or argv[0] not in ("write", "check"):
        print(__doc__); return 2
    cmd, stage = argv[0], os.path.abspath(argv[1]); origin = ""; extras = []; seconds = 0; max_age = 3600; i = 2
    while i < len(argv):
        if argv[i] == "--origin" and i + 1 < len(argv): origin = argv[i + 1]; i += 2
        elif argv[i] == "--extra" and i + 1 < len(argv): extras.append(argv[i + 1]); i += 2
        elif argv[i] == "--seconds" and i + 1 < len(argv): seconds = int(argv[i + 1]); i += 2
        elif argv[i] == "--max-age" and i + 1 < len(argv): max_age = int(argv[i + 1]); i += 2
        else: print("REFUSED: unknown argument " + argv[i], file=sys.stderr); return 2
    if not os.path.isdir(stage): print("REFUSED: not a directory: " + stage, file=sys.stderr); return 2
    if cmd == "write": write(stage, origin, extras, seconds); print("receipt written for %s" % stage); return 0
    ok, why = check(stage, origin, extras, max_age); print(("valid: " if ok else "not valid: ") + why); return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
