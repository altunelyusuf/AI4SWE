#!/usr/bin/env python3
"""oe_release_v1_7_0 - the release path in ONE command: gates, manifest, dry-run, publish, wait for CI and the tag (plan v1.16.0, owner 2026-10-07).

The governing session lost most of its time not to the checks but to the hand-work around them: a test run that left bytecode (a stowaway), a manifest written
by a private script, a deletion list worked out by trial, a re-run of a refusal that had not been fixed, a wait for CI by polling. Every check stays; this runs
them in the right order, once, and says what to do when one refuses.

  python3 oe_release_v1_7_0.py <stage> <package-slug> [--publish] [--expect-delete FILE] [--expect-rewrite FILE] [--deletions-file OUT] [--cause "<text>"]
                               [--step-timeout SECONDS] [--no-wait]

Needs OE_SESSION in the environment and a token in GH_TOKEN (passed on, never printed). Steps, each with a time limit and its duration reported:
  1 manifest  oe_manifest: bytecode and the record removed, manifest written and verified both ways (first, because the package gates verify it)
  2 gates     the package's own release check and knowledge-base guard when the stage ships them (run without writing bytecode); the manifest is then written once more
  0  export    (v1.5.0) a stage with SHIPPED_TOOLS.txt gets its operating tools refreshed from repo-tooling (oe_export_tools), names replaced
  2  gates     (v1.4.0) a stage with 03-tooling/GATES_FROM.txt naming a sibling package (oe-method) runs that package's release check on the stage; an unnamed or missing source refuses
  2c manifest gate  CI's Gate 0 on the stage alone, nested manifests included (v1.3.0, plan task 27); a stale nested manifest is caught here, not after the push
  2b aggregate the debt aggregate's own --verify, as CI runs it, on the clone with the stage put in the package's place (v1.2.0); a register line the generator refuses is caught here, not after the push
  3 dry-run   the publisher with --dry-run; it runs every check the real publish runs
  4 publish   (only with --publish) the manifest again (a dry-run can leave bytecode in the stage), then the publisher for real, then wait inside this command for the CI run of the new commit and for the release tag
A refusal by the publisher's deletion guard writes the deletions it found to --deletions-file (default <stage>.deletions.txt, outside the stage): read them; if each
is meant, rerun with --expect-delete <that file>. Nothing is accepted for you.

v1.3.0 (plan task 27; reported by the a domain ecosystem session, 2026-10-12): the top-level manifest step did not run CI's Gate 0, so a nested stage manifest still listing retired files passed every step here and turned CI red after the push. Step 2c runs oe_manifest_gate on the stage alone (nested manifests included); NOT RUN is said loudly when the gate is not in the clone.
v1.2.0 (plan task 24; reported by the a domain ecosystem session, 2026-10-12): the dry-run did not run `oe_debt_aggregate --verify`, which CI runs on every push, so a register line the generator refuses (an opt-in
line with no recorded ruling) passed every step here and turned CI red after the push. Step 2b runs it on the clone with the stage in the package's place; a refusal stops the release, growth and a new line fail,
a mere shrink is a warning, exactly as in CI. If neither the aggregate tool nor the aggregate file is found anywhere it says NOT RUN loudly (a check that found nothing must not read as a pass); if only one is missing it refuses.
v1.1.2: a CI run that GitHub cancelled because a newer run of the same commit replaced it is not counted (v1.1.0 reported "CI RED" for a commit whose replacing run was green).
v1.1.0 (plan v1.17.0, rule R9): a package's own gate may take many minutes, so the dry-run and publish steps default to 1800 s (checks stay 280 s; --step-timeout overrides both);
the stage's ledger keeps each step's duration and the next run prints "last time ... expect about N s" before it starts (rule R5); the summary says when the publisher
reused the dry-run's gate receipt instead of running the gates a second time.
v1.0.1: the manifest is written FIRST and once more after the gates: the package's release check verifies the manifest, so v1.0.0 (gates first) refused the pack at its first real use; the order is now tested with a gate that needs the manifest.

The root-cause rule (discipline v2.16.0, rule R3): the same refusal twice in a row for one stage stops the command (exit 3) until you pass --cause "<what was
wrong and what you changed>"; the cause is kept in <stage>.oe_release_ledger.json beside the stage. A step that exceeds its time limit stops with exit 4 and
says not to run it again unchanged.

Exit codes: 0 done; 1 a step refused (its last lines and the fix are printed); 2 usage or environment; 3 repeated refusal, cause required; 4 time limit."""
import glob, json, os, re, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))


def vkey(p):
    return [int(x) for x in re.findall(r"\d+", os.path.basename(p))]


def tool(pattern):
    c = sorted(glob.glob(os.path.join(HERE, pattern)), key=vkey)
    c = [x for x in c if "_test_" not in x]
    return c[-1] if c else None


def run(cmd, timeout, cwd=None, env=None):
    t = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd, env=env)
        return r.returncode, (r.stdout or "") + (r.stderr or ""), time.time() - t, False
    except subprocess.TimeoutExpired as e:
        out = ((e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")) + ((e.stderr or b"").decode() if isinstance(e.stderr, bytes) else (e.stderr or ""))
        return 124, out, time.time() - t, True


def refusal_line(out):
    m = re.findall(r"^REFUSED: .*$|^FAIL.*$|^VERDICT: FAIL.*$", out, re.M)
    return m[0][:300] if m else ""


def deletions_in(out):
    """the paths the wholesale-replace guard listed (five spaces of indent after its header)"""
    paths = []; on = False
    for ln in out.splitlines():
        if "wholesale-replace guard:" in ln and "exist at origin" in ln: on = True; continue
        if on:
            if ln.startswith("     ") and ln.strip(): paths.append(ln.strip())
            elif paths: break
    return paths


def aggregate_check(stage, slug, clone, env, timeout):
    """CI's `oe_debt_aggregate --verify`, run before the push: the clone's tree with the stage in the package's place. Returns (status, rc, output, seconds, timed_out); status is 'run' or 'not run'."""
    root = tempfile.mkdtemp(prefix="oe_agg_")
    try:
        for d in os.listdir(clone):
            if d.startswith(".") or d == slug or not os.path.isdir(os.path.join(clone, d)): continue
            os.symlink(os.path.join(clone, d), os.path.join(root, d))
        os.symlink(os.path.abspath(stage), os.path.join(root, slug))
        reg = sorted(glob.glob(os.path.join(root, "oe-pack", "04-documentation", "structure-debt", "STRUCTURE_DEBT_AGGREGATE_v*.tsv")), key=vkey)
        ag = [x for x in sorted(glob.glob(os.path.join(root, "repo-tooling", "oe_debt_aggregate_v*.py")), key=vkey) if "_test_" not in x]
        if not reg and not ag: return "not run", 0, "no debt aggregate tool and no aggregate file in the clone or the stage", 0.0, False
        if not reg or not ag:
            return "run", 1, "REFUSED: the debt aggregate check is half there (%s missing): fix the clone or the stage" % ("the aggregate file" if not reg else "the aggregate tool"), 0.0, False
        rc, out, dt, to = run([sys.executable, "-B", ag[-1], ".", "--previous", reg[-1], "--verify"], timeout, cwd=root, env=env)
        return "run", rc, out, dt, to
    finally:
        shutil.rmtree(root, ignore_errors=True)


def manifest_gate_check(stage, slug, clone, env, timeout):
    """CI's Gate 0 (`oe_manifest_gate`), run before the push on the stage alone, nested manifests included (a nested stage manifest that still listed retired files passed
    the top-level manifest step and turned CI red after the push: reported by the a domain ecosystem session, plan task 27). Only the stage is scanned, so another package's state never blocks this release."""
    gate = tool_in(clone, "oe_manifest_gate_v*.py")
    if not gate: return "not run", 0, "no oe_manifest_gate in the clone", 0.0, False
    root = tempfile.mkdtemp(prefix="oe_mg_")
    try:
        os.symlink(os.path.abspath(stage), os.path.join(root, slug))
        rc, out, dt, to = run([sys.executable, "-B", gate, root], timeout, cwd=root, env=env)
        return "run", rc, out, dt, to
    finally:
        shutil.rmtree(root, ignore_errors=True)


def tool_in(clone, pat):
    c = [x for x in sorted(glob.glob(os.path.join(clone, "repo-tooling", pat)), key=vkey) if "_test_" not in x]
    return c[-1] if c else None


def load_ledger(p):
    try: return json.load(open(p))
    except Exception: return {"count": {}, "causes": []}


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 2
    stage = os.path.abspath(argv[0]); slug = argv[1] if len(argv) > 1 else None
    opt = {"publish": False, "expect": None, "rewrite": None, "dfile": None, "cause": None, "timeout": None, "wait": True, "publisher": None, "clone": None}
    i = 2
    while i < len(argv):
        a = argv[i]
        if a == "--publish": opt["publish"] = True; i += 1
        elif a == "--no-wait": opt["wait"] = False; i += 1
        elif a in ("--expect-delete", "--expect-rewrite", "--deletions-file", "--cause", "--step-timeout", "--publisher", "--clone") and i + 1 < len(argv):
            k = {"--expect-delete": "expect", "--expect-rewrite": "rewrite", "--deletions-file": "dfile", "--cause": "cause", "--step-timeout": "timeout", "--publisher": "publisher", "--clone": "clone"}[a]
            opt[k] = int(argv[i + 1]) if k == "timeout" else argv[i + 1]; i += 2
        else: print("REFUSED: unknown argument " + a, file=sys.stderr); return 2
    token = os.environ.get("GH_TOKEN") or os.environ.get("GH_PAT")
    if not slug or not os.path.isfile(os.path.join(stage, "VERSION.txt")) or not os.environ.get("OE_SESSION") or not token:
        print("REFUSED: needs <stage with VERSION.txt> <slug>, OE_SESSION and GH_TOKEN in the environment", file=sys.stderr); return 2
    publisher = opt["publisher"] or tool("oe_publish_v*.sh"); manifest = tool("oe_manifest_v*.py")
    clone = opt["clone"] or os.path.dirname(HERE)
    if not publisher or not manifest: print("REFUSED: oe_publish and oe_manifest must sit beside this tool", file=sys.stderr); return 2
    T_CHECK = opt["timeout"] or 280; T_PUB = opt["timeout"] or 1800      # a package's own gate may legitimately take many minutes (rule R9); --step-timeout overrides both
    ledger_p = stage.rstrip("/") + ".oe_release_ledger.json"; L = load_ledger(ledger_p)
    stuck = [fp for fp, n in L["count"].items() if n >= 2]
    if stuck and not opt["cause"]:
        print("STOP (rule R3): the same refusal came twice for this stage:\n  %s\nWrite what was wrong and what you changed, and rerun with --cause \"<text>\". Do not run it a third time unchanged." % stuck[0], file=sys.stderr)
        return 3
    if opt["cause"]:
        L["causes"].append({"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "cause": opt["cause"]}); L["count"] = {}
    env = dict(os.environ); env["GH_PAT"] = token; env["PYTHONDONTWRITEBYTECODE"] = "1"
    t0 = time.time(); steps = []
    last = L.get("durations")
    if last: print("last time for this stage: " + ", ".join("%s %.0fs" % kv for kv in last.items()) + " -- expect about %.0fs in all (rule R5: say so before you wait)" % sum(last.values()), flush=True)
    else: print("first run for this stage: no earlier timing; limits: checks %ds, publisher steps %ds" % (T_CHECK, T_PUB), flush=True)
    if opt["publish"]:
        print("a publish waits for CI and the tag, usually 2 to 5 minutes: if your caller limits one command to about 2 minutes (a tool call), run this in the background and read its log (nohup ... > <log> 2>&1 &); a call that is cut off does not undo a publish that already began (plan task 19)", flush=True)
    def remember():
        L["durations"] = {n: round(d) for n, d in steps}; json.dump(L, open(ledger_p, "w"))
    def refuse(name, out, rc):
        fp = refusal_line(out) or "%s exited %d" % (name, rc)
        L["count"][fp] = L["count"].get(fp, 0) + 1; json.dump(L, open(ledger_p, "w"))
        print("\n".join(out.strip().splitlines()[-12:])); print("-- %s refused (%s)" % (name, fp))
        return 1
    def timed_out(name):
        limit = T_PUB if name in ("dry-run", "publish") else T_CHECK
        print("STOP: %s exceeded its %ds limit. Do not run it again unchanged: find what it waits on (a network call, a lock, a very large stage) and fix that first." % (name, limit), file=sys.stderr)
        return 4
    # 0 export (v1.5.0): an edition stage that lists SHIPPED_TOOLS.txt gets its operating tools refreshed from repo-tooling, names replaced, before anything is checked
    if os.path.isfile(os.path.join(stage, "SHIPPED_TOOLS.txt")):
        exp = tool_in(clone, "oe_export_tools_v*.py")
        if not exp:
            print("REFUSED: the stage lists SHIPPED_TOOLS.txt but oe_export_tools is not in repo-tooling of the clone", file=sys.stderr); return 2
        rc, out, dt, to = run([sys.executable, "-B", exp, stage, os.path.join(clone, "repo-tooling")], 120, env=env); steps.append(("export tools", dt))
        if to: return timed_out("export tools")
        if rc != 0: return refuse("export tools", out, rc)
        print("export tools: " + out.strip().splitlines()[-1], flush=True)
    # 1 manifest (first: the package gates verify the manifest)
    rc, out, dt, to = run([sys.executable, "-B", manifest, stage], 120, env=env); steps.append(("manifest", dt))
    if to: return timed_out("manifest")
    if rc != 0: return refuse("manifest", out, rc)
    # 2 gates
    from_decl = os.path.join(stage, "03-tooling", "GATES_FROM.txt")      # v1.4.0: a package that keeps no gate of its own names where it is authored
    from_pkg = open(from_decl).read().strip() if os.path.isfile(from_decl) else None
    for pat, label in (("03-tooling/release_check_v*.py", "release check"), ("03-tooling/kb_integrity_guard_v*.py", "knowledge-base guard")):
        c = sorted(glob.glob(os.path.join(stage, pat)), key=vkey)
        if not c and from_pkg and "release_check" in pat:
            c = sorted(glob.glob(os.path.join(clone, from_pkg, pat)), key=vkey)
            if not c:
                print("REFUSED: 03-tooling/GATES_FROM.txt names %s, but %s/%s is not in the clone: a gate a release can skip is not a control" % (from_pkg, from_pkg, pat), file=sys.stderr)
                return refuse(label, "REFUSED: gate source %s not found" % from_pkg, 1)
            print("release check: taken from %s (this stage ships none; GATES_FROM.txt)" % from_pkg, flush=True)
        if not c: continue
        args = [sys.executable, "-B", c[-1]] + (["."] if "release_check" in pat else [])
        cenv = env
        if "release_check" in pat:      # v1.7.0: a stage's own configuration (recorded ceilings of its registrants) is handed to a release check taken from another package
            cf = sorted(glob.glob(os.path.join(stage, "03-tooling", "release_check_config_v*.json")), key=vkey)
            if cf: cenv = dict(env); cenv["RELEASE_CHECK_CONFIG"] = cf[-1]
        rc, out, dt, to = run(args, T_CHECK, cwd=stage, env=cenv); steps.append((label, dt))
        if to: return timed_out(label)
        if rc != 0: return refuse(label, out, rc)
    rc, out, dt, to = run([sys.executable, "-B", manifest, stage], 120, env=env)   # the gates may have touched the stage: write and verify once more
    if to: return timed_out("manifest")
    if rc != 0: return refuse("manifest", out, rc)
    # 2b the debt aggregate, as CI runs it (a refused register line passes everything else here and fails after the push)
    st, rc, out, dt, to = aggregate_check(stage, slug, clone, env, T_CHECK)
    if st == "not run": print("debt aggregate check: NOT RUN (%s)" % out, flush=True)
    else:
        steps.append(("debt aggregate", dt))
        if to: return timed_out("debt aggregate")
        if rc != 0: return refuse("debt aggregate", out, rc)
        warn = [l for l in out.splitlines() if "WARNING" in l]
        if warn: print("debt aggregate check: " + warn[0].strip(), flush=True)
    # 2c Gate 0 on the stage, nested manifests included (plan task 27)
    st, rc, out, dt, to = manifest_gate_check(stage, slug, clone, env, T_CHECK)
    if st == "not run": print("manifest gate check: NOT RUN (%s)" % out, flush=True)
    else:
        steps.append(("manifest gate", dt))
        if to: return timed_out("manifest gate")
        if rc != 0: return refuse("manifest gate", out, rc)
    # 3 dry-run (and 4 publish)
    base = ["bash", publisher, token, stage, slug]
    if opt["expect"]: base += ["--expect-delete", opt["expect"]]
    if opt["rewrite"]: base += ["--expect-rewrite", opt["rewrite"]]      # v1.6.0: a same-name rewrite that is meant, named in a file, passed to the publisher
    rc, out, dt, to = run(base + ["--dry-run"], T_PUB, cwd=clone, env=env); steps.append(("dry-run", dt))
    if to: return timed_out("dry-run")
    if rc != 0:
        gone = deletions_in(out)
        if gone:
            df = opt["dfile"] or stage.rstrip("/") + ".deletions.txt"; open(df, "w").write("\n".join(gone) + "\n")
            print("-- the deletion guard found %d deletion(s); written to %s. Read them; if each one is meant, rerun with --expect-delete %s" % (len(gone), df, df))
        return refuse("dry-run", out, rc)
    L["count"] = {}; remember(); reused = "reused receipt" in out
    summary = "checks pass; dry-run passes" + ("; the package's own gates were not run again (receipt reused)" if reused else "")
    if opt["publish"]:
        # the dry-run itself can leave bytecode in the stage when the tools being published sit in it (found publishing repo-tooling with this very command): clean again
        rc, out, dt, to = run([sys.executable, "-B", manifest, stage], 120, env=env)
        if to: return timed_out("manifest")
        if rc != 0: return refuse("manifest", out, rc)
        rc, out, dt, to = run(base, T_PUB, cwd=clone, env=env); steps.append(("publish", dt))
        if to: return timed_out("publish")
        m = re.search(r"^published: (\S+) v(\S+)\s+\(tag \S+ left to the workflow, commit (\w+)\)", out, re.M)
        if rc != 0 or not m: return refuse("publish", out, rc)
        remember(); pkg, ver, sha = m.groups(); summary = "published %s v%s (commit %s)%s" % (pkg, ver, sha, "; gates reused the dry-run's receipt" if "reused receipt" in out else "")
        if opt["wait"]:
            subprocess.run(["git", "-C", clone, "pull", "-q", "--ff-only"], capture_output=True, text=True)
            full = subprocess.run(["git", "-C", clone, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
            state = "no CI run seen"; end = time.time() + 420
            while time.time() < end:
                r = subprocess.run(["gh", "api", "repos/your-account/Ontologies/actions/runs?per_page=12", "--jq", '[.workflow_runs[]|select(.head_sha=="%s" and .name=="OE gates")|[.status,.conclusion]]' % full], capture_output=True, text=True)
                try: runs = json.loads(r.stdout or "[]")
                except Exception: runs = []
                runs = [x for x in runs if x[1] != "cancelled"]      # GitHub cancels a run that a newer run of the same commit replaces; a cancelled run says nothing about the commit
                if runs and all(x[0] == "completed" for x in runs):
                    state = "CI " + ("green" if all(x[1] == "success" for x in runs) else "RED"); break
                time.sleep(15)
            tag = "%s-v%s" % (pkg, ver); lt = subprocess.run(["git", "-C", clone, "ls-remote", "--tags", "origin", "refs/tags/" + tag], capture_output=True, text=True).stdout
            summary += "; %s; tag %s %s" % (state, tag, "present" if tag in lt else "not yet there (the workflow makes it)")
    print("steps: " + ", ".join("%s %.0fs" % s for s in steps)); print("release: %s; total %.0fs" % (summary, time.time() - t0))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
