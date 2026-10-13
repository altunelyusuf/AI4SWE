#!/usr/bin/env python3
"""oe_ceremony_digest_v1_1_0 - the ceremony's read of the OE discipline, smaller and still strict.

Prints, for the highest-versioned OE discipline file under ROOT (default .): its name, SHA-256 prefix and size;
every rule section IN FULL; each change-history section as its heading and size only (--full prints it too);
the label (labels before identifiers) of every lesson or practice cited ONLY in the change history, so no cited
rule drops out of view; the knowledge base's lesson count (--lessons prints one label line each); and, when
the OE inbox is present, its pending items.

Strictness is checked, not assumed: the two rules that used to live only in the change history (the knowledge
base is authoritative; corrections are appended notes) must now be present OUTSIDE it. If either is missing the
digest prints RULES CHECK: FAIL and exits 1 -- in that case read the file with --full. Origin: a parallel session's
proposal (2026-10-05, measured 8,364 + 6,125 tokens for rules vs history), adopted under the owner's ruling the same day;
this file is re-written and tested here, not copied from that proposal's worked copy.

Usage: oe_ceremony_digest_v1_1_0.py [ROOT] [--full] [--lessons] [--discipline FILE]
Exit: 0 digest printed and rules check OK; 1 rules check failed; 2 nothing found to read (refused, never an empty digest)."""
import glob, hashlib, os, re, sys

REQUIRED = (("the knowledge base governs when lesson text and the discipline diverge", "the ABox is authoritative"),
            ("a historical record is corrected by an appended note", "appended note, not by rewriting"))


def newest(root, pats):
    fs = [f for p in pats for f in glob.glob(os.path.join(root, p))]
    if not fs:
        return None
    return max(fs, key=lambda f: [int(x) for x in re.findall(r"_v(\d+)_(\d+)_(\d+)", os.path.basename(f))[-1]])


def split(text):
    parts = re.split(r"(?m)^(#{1,3} .*)$", text)
    return [(parts[0], "")] + list(zip(parts[1::2], parts[2::2]))


def is_history(h):
    return bool(re.match(r"## v\d", h))


def main(argv):
    pos = [a for a in argv if not a.startswith("-")]
    full, lessons = "--full" in argv, "--lessons" in argv
    disc_arg = argv[argv.index("--discipline") + 1] if "--discipline" in argv else None
    if disc_arg:
        pos = [a for a in pos if a != disc_arg]
    root = pos[0] if pos else "."
    D = disc_arg or newest(root, ["oe-method/04-documentation/OE_Operating_Discipline_v*.md",
                                  "04-documentation/OE_Operating_Discipline_v*.md"])
    if not D:
        print("REFUSED: no OE_Operating_Discipline_v*.md found under " + root, file=sys.stderr)
        return 2
    raw = open(D, "rb").read()
    secs = split(raw.decode("utf-8"))
    print(f"DISCIPLINE {os.path.basename(D)} sha256 {hashlib.sha256(raw).hexdigest()[:8]} {len(raw):,} B")
    rules = "".join(h + b for h, b in secs if not is_history(h))
    hist = "".join(h + b for h, b in secs if is_history(h))
    for h, b in secs:
        if full or not is_history(h):
            sys.stdout.write(h + b)
        else:
            print(f"{h}  [change history, {len((h + b).encode()):,} B, not printed; --full prints it]")
    missing = [name for name, phrase in REQUIRED if phrase not in rules]
    if missing:
        print("\nRULES CHECK: FAIL -- not found outside the change history: " + "; ".join(missing) + ". Read the file with --full.")
    else:
        print(f"\nRULES CHECK: OK -- {len(REQUIRED)}/{len(REQUIRED)} formerly history-only rules are in the rule sections")
    # v1.1.0: the knowledge base is found by content in either layout (own file, or a module of the governance unit's A-Box)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from oe_resolve_v1_0_0 import resolve_kb
    KB = None
    for pk in ("oe-method", "oe-pack", "."):
        KB = resolve_kb(os.path.join(root, pk))
        if KB: break
    if KB:
        import rdflib
        g = rdflib.Graph(); g.parse(KB)
        labels = {}
        for i, l in g.query("""PREFIX kb: <http://example.org/knowledge-base#> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                               SELECT ?id ?l WHERE { ?s kb:hasLessonId ?id . OPTIONAL { ?s rdfs:label ?l } }"""):
            labels.setdefault(str(i), re.sub(r"^\S+-\S+: ", "", str(l)) if l else "(no label)")
        for (l,) in g.query("""PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                               SELECT ?l WHERE { ?s rdfs:label ?l . FILTER(STRSTARTS(STR(?l), "BP-")) }"""):
            k, _, v = str(l).partition(": ")
            labels.setdefault(k, v or str(l))
        ids = lambda s: set(re.findall(r"\b(?:L-\d+|BP-[A-Z]?\d+)\b", s))
        only = sorted(ids(hist) - ids(rules), key=lambda x: (x[:2], len(x), x))
        print(f"\nCITED ONLY IN THE CHANGE HISTORY ({len(only)}), with their labels:")
        for i in only:
            print(f"  {labels.get(i, '(NOT FOUND in the knowledge base)')} ({i})")
        les = sorted(((k, v) for k, v in labels.items() if k.startswith("L-")), key=lambda kv: (len(kv[0]), kv[0]))
        print(f"\nKNOWLEDGE BASE {os.path.relpath(KB, root)} sha256 {hashlib.sha256(open(KB, 'rb').read()).hexdigest()[:8]}: {len(les)} lessons"
              + ("" if lessons else " (labels not printed; --lessons prints one line each)"))
        if lessons:
            for k, v in les:
                print(f"  {v} ({k})")
    else:
        print("\nKNOWLEDGE BASE: not found under " + root + " (the lesson labels cited only in the history are not shown)")
    P = os.path.join(root, "oe-pack/07-handover-inbox/pending")
    if os.path.isdir(P):
        items = sorted(f for f in os.listdir(P) if f != "README.md")
        print("\nOE INBOX pending:", ", ".join(items) or "none")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
