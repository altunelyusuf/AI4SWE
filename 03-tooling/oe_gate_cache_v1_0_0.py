#!/usr/bin/env python3
"""oe_gate_cache_v1_0_0 - run a deterministic check once per set of bytes, for a package's own gate steps (plan v1.17.0).

A package gate that validates the whole data and rules files several times (each step, each release, the dry-run and the publish) pays the full cost every time
although nothing it reads has changed. Wrap such a step in this tool and it is run once for each distinct set of inputs:

  python3 oe_gate_cache_v1_0_0.py run --key-file data_v1_2_0.ttl --key-file rules/ --key-text "profile=full" [--max-age 86400] [--cache-dir DIR] -- <command ...>

The key is the sha256 of: the command (every word), the bytes of every --key-file (a directory counts as the digest of its tree), every --key-text, and the
Python version. If a PASS with the same key exists and is not older than --max-age (default 24 h) the stored output is printed with a line saying it was reused, and
the exit code is 0 without running anything. Otherwise the command runs, its output is shown as usual, and ONLY a pass (exit 0) is stored. A failure is never
stored, so a failing step is re-run every time. OE_NO_GATE_CACHE=1 or --no-cache forces a run.

THE RULE THAT KEEPS IT SOUND: a step may be cached only if everything it reads is named in --key-file or --key-text. A step that reads the network, the clock, a
database, an environment variable or a file that is not named is NOT deterministic in this sense and must not be wrapped. Name the checker script itself as a
--key-file, so that changing the check changes the key. The cache lives outside the package (default ~/.cache/oe_gate_cache, or OE_GATE_CACHE_DIR).

Exit codes: the wrapped command's own code (0 on reuse); 2 usage."""
import hashlib, json, os, subprocess, sys, time


def digest(path):
    h = hashlib.sha256()
    if os.path.isdir(path):
        rows = []
        for r, ds, fs in os.walk(path):
            ds[:] = sorted(d for d in ds if d not in (".git", "__pycache__"))
            for f in fs:
                if f.endswith(".pyc"): continue
                p = os.path.join(r, f); rows.append("%s\t%s" % (os.path.relpath(p, path), digest(p)))
        h.update("\n".join(sorted(rows)).encode())
    else:
        with open(path, "rb") as fh:
            for ch in iter(lambda: fh.read(1 << 20), b""): h.update(ch)
    return h.hexdigest()


def key_of(cmd, files, texts):
    h = hashlib.sha256()
    for part in (["cmd"] + list(cmd) + ["files"] + ["%s=%s" % (f, digest(f)) for f in files] + ["texts"] + list(texts) + ["py", sys.version.split()[0]]):
        h.update(part.encode()); h.update(b"\0")
    return h.hexdigest()


def main(argv):
    if not argv or argv[0] != "run" or "--" not in argv:
        print(__doc__); return 2
    split = argv.index("--"); opts, cmd = argv[1:split], argv[split + 1:]
    files, texts = [], []; max_age = 86400; cdir = os.environ.get("OE_GATE_CACHE_DIR") or os.path.expanduser("~/.cache/oe_gate_cache"); nocache = bool(os.environ.get("OE_NO_GATE_CACHE")); i = 0
    while i < len(opts):
        if opts[i] == "--key-file" and i + 1 < len(opts): files.append(opts[i + 1]); i += 2
        elif opts[i] == "--key-text" and i + 1 < len(opts): texts.append(opts[i + 1]); i += 2
        elif opts[i] == "--max-age" and i + 1 < len(opts): max_age = int(opts[i + 1]); i += 2
        elif opts[i] == "--cache-dir" and i + 1 < len(opts): cdir = opts[i + 1]; i += 2
        elif opts[i] == "--no-cache": nocache = True; i += 1
        else: print("REFUSED: unknown argument " + opts[i], file=sys.stderr); return 2
    if not cmd or not files:
        print("REFUSED: needs at least one --key-file (name what the command reads) and a command after --", file=sys.stderr); return 2
    missing = [f for f in files if not os.path.exists(f)]
    if missing: print("REFUSED: --key-file not found: " + ", ".join(missing), file=sys.stderr); return 2
    key = key_of(cmd, files, texts); entry = os.path.join(cdir, key + ".json")
    if not nocache and os.path.isfile(entry):
        try: e = json.load(open(entry))
        except Exception: e = None
        if e and time.time() - e.get("written", 0) <= max_age:
            sys.stdout.write(e.get("output", ""))
            print("[gate cache] reused: a pass on these exact inputs %d s ago (took %.0f s); key %s" % (time.time() - e["written"], e.get("seconds", 0), key[:12])); return 0
    t = time.time(); r = subprocess.run(cmd, capture_output=True, text=True); dt = time.time() - t
    sys.stdout.write(r.stdout); sys.stderr.write(r.stderr)
    if r.returncode == 0 and not nocache:
        os.makedirs(cdir, exist_ok=True)
        json.dump({"key": key, "output": r.stdout, "written": time.time(), "seconds": dt, "cmd": cmd}, open(entry, "w"))
        print("[gate cache] stored a pass; key %s" % key[:12])
    return r.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
