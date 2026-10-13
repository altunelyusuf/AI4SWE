# Handbook

Every rule here exists because something went wrong. This document pairs each with the failure it
prevents, because a rule whose cost you can see but whose benefit you cannot will be abandoned the
first time it is inconvenient.

The knowledge base holds 175 entries — 59 best practices and 116 lessons. This handbook covers the
load-bearing ones. The rest are in `01-vocabularies/knowledge_base_abox_v*.ttl`, each carrying its
own definition and the kind of case that produced it.

---

## 1. The bytes govern

**BP-D2 — never trust summaries.** Closure notes, changelogs, READMEs and conversational
summaries state what their author *intended* to ship. The artifact may differ.

The failure: someone writes "all gates pass, 91/91 documented" and it becomes true by repetition.
Three sittings later a decision rests on a number nobody measured. In this method's own history a
changelog reported 32 undocumented classes where the shipped tool reproduced 29 — the defect was
real, the headline figure was not reproducible, and it had been quoted forward.

The practice: before repeating a number, run the thing that produces it. This costs seconds and is
the single highest-yield habit in the method.

**L-65 / L-66 — verify before you claim.** Extended in practice to cover *analytical
characterisations*, not just figures. "This is essentially the same as X" grounds a decision as
much as a count does, and needs the same check first.

## 2. A changed artifact gets a new version

**BP-D7.** New bytes, new version token — in the filename, in `VERSION.txt`, and in
`owl:versionInfo`. All three.

The failure is quiet. A file gains a status banner, a typo fix, one clarifying sentence, and keeps
its `v1_0_0` name. Now two different byte-states share one identity, and any statement of the form
"we reviewed v1.0.0" is ambiguous forever. It cannot be repaired retrospectively — you cannot
determine which one was reviewed.

This is the most frequently violated rule in the method's own history, by the method's own
maintainers, repeatedly. That is not an argument against it. It is why the version identity check
runs as an automated gate rather than as a habit.

## 3. A gate that cannot fail verifies nothing

**L-95.** Every gate ships with a negative fixture: input it must reject. A gate that has only
seen data it accepts is decorative — it produces the feeling of verification with none of the
substance.

This has repeatedly caught real defects in this method's own tooling:

- A SHACL shape whose `sh:in` used plain literals where the data used typed ones. It rejected
  *every* conformant record. Only the positive control revealed it — the negative fixtures all
  "passed" by failing for the wrong reason.
- A cleanliness check using `\bNAME\b` that could not match `NAME_notes.md`, because underscore is
  a word character. Underscores are this method's own filename convention. A file named after the
  very thing being excluded would have passed.

Both were found by fixtures, not by reading. Reading your own gate confirms what you meant; running
it against known-bad input confirms what it does.

## 4. Resolve by highest version, never by name

Callers glob and sort: `ls thing_v*.ttl | sort -V | tail -1`. Never hard-code `thing_v1_2_0.ttl`.

Two failures. A hard-coded reference silently keeps using an old file after a bump — no error, just
stale behaviour. And `head -1` or plain `sort` is not version ordering: lexicographically `v1_0_0`
precedes `v2_0_0`, so "first" gives you the *oldest*. Use `sort -V`.

## 5. Three kinds of file, three different rules

**L-112.** Before any corpus-wide edit, classify:

| Class | Examples | Rule |
|---|---|---|
| **Current-state descriptions** | vocabularies, shapes, tools, READMEs | editable — the actual target |
| **Historical records** | changelogs, release notes, dated assessments, git history | never rewritten; corrected by *appending* a dated correction |
| **Generated artifacts** | manifests, computed reports | never hand-edited; **regenerated** |

A global search-and-replace is correct per-occurrence and still corrupts the record. Rewriting a
changelog entry to name the current version does not update it — it makes it false, and
undetectably so, because the text reads as though it was always there.

The third class was added *after* the two-class version shipped, when a tool implementing the rule
correctly flagged a manifest as editable. A manifest is not a record of the past, so the two-way
split was wrong — not the tool. Corrections to a rule are themselves evidence and get recorded.

## 6. Don't build structure on one case

**L-110.** When a case does not fit an existing governed term, three responses exist: mint a
sibling term, mint an exception, or enrich the existing definition. On one producer's evidence the
first two are premature. A term created to cover one case encodes that case's incidental properties
as general, and the next genuinely different case then strains it or forces a third.

Enrich the term instead, and wait. The structure can still be minted later, when a second divergent
case shows where the boundary actually belongs.

**Not a general preference for inaction.** Where a case diverges in *form* — a different filename
shape, a different artifact kind — the new term is correct and deferring hides the divergence. The
test is whether the case follows the existing pattern and differs only in a fact *about* its usage.

**L-71** is the mirror: a class minted and left unpopulated. Recording an empty or duplicate rule to
satisfy a checklist is the opposite failure to forgetting one, and equally damaging.

## 7. Record what you learn, and only that

**L-84.** When something genuinely new emerges, record it with its evidence. Duplicate-screen first
against every existing entry — if it is already covered, cite the existing rule instead.

The judgement is real in both directions. Padding the catalogue to close a session is a failure.
So is withholding a genuine lesson because the round felt finished — which happened here, and the
lesson was adopted over its author's own decision not to submit it.

## 8. Nothing persists but the files

**L-85.** Between sittings, assume the working environment is gone — including your tools.
Rehydrate from the package, re-verify the manifest, re-run the validators, and confirm the version
markers before any governed action.

This is written for AI sessions with no memory. It applies unchanged to a person returning after
three months, which is the same problem with a slower clock.

## 9. Ownership: propose, don't mutate

When several people or sessions work on one repository, each owns specific packages. A finding
about someone else's package is *raised*, not fixed in place. The owner decides versioning.

Without this, two well-intentioned corrections produce a package whose version history no longer
describes its content.

---

## The honest cost

For a fifty-triple ontology you will maintain alone for a month, this is overhead with no payoff.
Use a file and a backup.

It starts paying when any of these is true: the work outlives your memory of it; more than one
person or session touches it; someone must trust a claim about it without re-deriving it; or it
must be handed over.

It also assumes something about you: that you would rather be told you are wrong by a script than
find out later, and that you will record the times you were. The method's own history contains
repeated violations by its own maintainers, caught by its own gates. That is what it looks like
working — not an embarrassment, but the evidence that the checks are load-bearing rather than
ornamental.
