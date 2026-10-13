# Use cases

Where this method earns its cost, where it does not, and what adopting it actually looks like.

---

## Not worth it

State this first, because a method that claims universal fit is making the same error as a test
that cannot fail.

- **A small ontology you maintain alone, short-term.** Fifty triples, one file, one person, a few
  weeks. Use a file and a backup. The gates would cost more than the errors they prevent.
- **Exploratory modelling.** While you are still deciding what the classes *are*, version discipline
  is friction against thinking. Adopt it when the model stabilises, not before.
- **A team that will not run the gates.** A gate everyone bypasses is worse than no gate: it
  produces a claim of verification with none of the substance. Better to adopt two rules honestly
  than ten nominally.

## Worth it when

Any one of these is enough:

- the work outlives your memory of it
- more than one person or session touches the same artifacts
- someone must trust a claim about it without re-deriving it
- it will be handed to somebody else

---

## Research group with a shared vocabulary

**The problem.** Four people, one domain ontology, no single owner. Two make compatible-looking
changes; the merge produces a class hierarchy neither intended. Nobody can say when the definition
of the central class last changed, or why.

**What the method supplies.** Package ownership with propose-don't-mutate: a finding about
someone else's module is raised, not fixed in place, and the owner decides the version. Every
change carries a version bump, so "when did this change" is answerable from the filenames alone.

**Adopt in this order:** version discipline (BP-D7) → manifest → ownership rule. SHACL gates last,
once the vocabulary is stable enough that constraints are not fighting the modelling.

---

## Graduate teaching

**The problem.** Twenty students submit ontologies. Grading consistency is hard to defend, and
"this could be better modelled" is not something a student can act on or appeal.

**What the method supplies.** The gates give a pass/fail that is not a matter of taste: does the
manifest verify, does the SHACL suite pass, does every class carry a definition. Students can run
exactly what you will run before they submit.

The higher-value lesson is **L-95**. Require every student to ship a negative fixture with their
constraints — input their own SHACL must reject. Most will discover that a constraint they were
confident in accepts everything. That single exercise teaches more about verification than a
lecture on it, and it transfers to every testing context they will meet later.

**Course shape that works:** week 1 the getting-started guide as a lab; assignments require a
verifying manifest and one proven-discriminating constraint; the final project adds a change
history where every version bump is justified.

**Watch for:** students gaming the manifest by regenerating it after breaking something. That is
itself a teachable moment about what a manifest does and does not prove — it proves the package is
internally consistent, not that it is correct.

---

## Thesis or multi-year project

**The problem.** Work spanning years in irregular sittings. You return after four months to a
directory of files with no reliable account of which is current, and a `notes.md` describing
decisions you can no longer verify.

**What the method supplies.** Version identity means the current file is identifiable without
memory. The manifest means you can tell whether anything drifted. BP-D2 means the summary in your
notes is treated as a claim to re-check rather than a fact — which is exactly right, because your
past self was optimistic.

**Adopt from day one.** Retrofitting version discipline onto three years of undated files is
substantially harder than starting with it, and the first year is when you feel the cost without
yet seeing the benefit.

---

## Industrial handover

**The problem.** A package must transfer to a team that was not there. "It passed our tests" is not
checkable by the receiving team, who cannot tell whether the tests could have failed.

**What the method supplies.** The receiving team runs the manifest check, the gates, and the
negative fixtures themselves. Every claim in the handover note is re-derivable rather than trusted.

**In practice** this converts handover from a meeting into a command. The publish record — a
machine-readable statement of what was verified, by which shape version, with the transcript
digest — means the acceptance conversation is about the artifact rather than about who remembers
what.

---

## Multi-agent and AI-assisted work

The case the method was actually forged in, so this section is description rather than projection.

**The problem.** An AI session has no memory of the last one. It receives a summary and treats it
as fact. It reuses a version token because nothing stopped it. It writes a gate that cannot fail
and reports success. Multiple sessions edit the same repository with no coordination.

**What the method supplies.** Every one of those failures has a rule and, more importantly, a gate.
The publisher re-executes the ceremony itself rather than accepting a session's report of it, which
is the load-bearing design decision: *you cannot publish by asserting that you verified*.

**The honest framing:** this is a discipline for work where the worker cannot remember. Whether
that worker is an AI session or a person returning after six months is a difference of degree.
Every rule here was written for the former and applies unchanged to the latter.

---

## Adoption ladder

You do not need all of it. In order of value per unit of friction:

1. **Version tokens in filenames** — cheapest, highest return. A changed file cannot hide.
2. **A self-verifying manifest** — one script; answers "is this what I built?"
3. **One negative fixture** — pick your most important check and prove it can fail.
4. **`VERSION.txt` and `owl:versionInfo` alignment** — makes half-finished edits detectable.
5. **SHACL gates in CI** — where the recurring cost starts paying back.
6. **Ownership and propose-don't-mutate** — once more than one party writes.
7. **The knowledge base** — record what you learn, screened against what is already there.

Stopping at step three is a legitimate outcome. Stopping there *honestly* — knowing which
guarantees you have and which you do not — is worth more than adopting all seven nominally.
