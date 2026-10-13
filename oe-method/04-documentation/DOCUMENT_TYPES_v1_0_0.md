# Document types

The method depends on three written artifacts that no other document in this package describes.
They are cheap to write, and each prevents a specific failure that gates cannot catch — because
each concerns a *decision*, and a decision has no bytes to verify.

Templates are generic. Fill them; do not rewrite them from memory each time.

---

## 1. Findings register

**What it is.** A living record of every known defect in a package: those open, those resolved and
in which version, and those deliberately deferred with a reason.

**The failure it prevents.** A defect is found, mentioned once, and forgotten. Three releases later
someone rediscovers it and spends a day establishing what is already known. Worse: a defect is
quietly deferred and later described as "resolved" because nobody wrote down which it was.

**Rules that make it work**

- One file per package, versioned like any other artifact (BP-D7). It changes constantly, so it
  will drift under a fixed version token unless you bump it.
- Findings get **stable identifiers** (`F-REL1`, `F-KB3`). An identifier survives rewording; a
  description does not.
- Every entry carries a **status and the version that changed it** — `OPEN`, `RESOLVED (v1.4.0)`,
  `PARTIALLY RESOLVED (v1.3.2)`, `DEFERRED`.
- **Partial resolution is its own status.** "Three of four closed, one deferred" is the honest
  state, and collapsing it to either RESOLVED or OPEN loses the part that matters.
- A deferred finding **must record why**, or it is indistinguishable from one that was forgotten.
- Never delete a resolved entry. The register is a historical record (L-112): it is appended to,
  not rewritten.

```markdown
# Known findings — as of vX.Y.Z

## F-<AREA><n> (<STATUS>) — <one-line summary>
**Found:** vA.B.C, by <how it surfaced: gate, review, adopter report>
**Effect:** <what breaks, or what claim becomes unreliable>
**Evidence:** <the command and its output, or the file and line>
**Disposition:** <resolved how, in which version — or deferred, and why>

## Resolved this arc
| ID | Summary | Closed in | How |
|----|---------|-----------|-----|

## Deferred
| ID | Summary | Reason for deferral | Revisit when |
```

---

## 2. Close-out report

**What it is.** Written at the end of a work arc: every item that was in scope, its final status,
and the reasoning. A scoreboard, not a narrative.

**The failure it prevents.** An arc ends with "we did most of it." Which parts, and why the rest
were dropped, exists only in memory — and memory is what this method assumes you do not have.

**Rules that make it work**

- **Every item gets a row**, including the ones that failed. A close-out listing only successes is
  advertising.
- The **reasoning column is the document**. `CLOSED` alone is unverifiable; `CLOSED — v2.6.0 → v2.7.0
  with external citations added` can be checked.
- **`PARTIALLY CLOSED` is a legitimate status** and usually the most informative one. Use it, and
  say which part remains.
- Anything not closed appears in the **findings register** before the arc ends. A close-out that
  discharges an open item by not mentioning it is the failure this document exists to prevent.
- Environment failures are recorded as failures, not omitted: *"could not run; environment bridge
  defect"* is a result.

```markdown
# <Package> <version arc> — Close-out report

## Scoreboard
| Item | Status | Reasoning |
|------|--------|-----------|
| <what was in scope> | CLOSED / PARTIALLY CLOSED / DEFERRED / FAILED | <what was done, in which version, verifiable how> |

## Deferred, with reasons
| Item | Why deferred | Where it is now tracked |
|------|--------------|-------------------------|

## Verification
<the gate output for this arc, quoted, not summarised>
```

---

## 3. Boundary record

**What it is.** A ratified statement of where one system's authority ends and another's begins,
written when two governed systems touch.

**The failure it prevents.** Two owners each believe a shared concern is theirs, or each believes it
is the other's. Both failures surface as a defect nobody fixes, discovered late and argued about
rather than resolved.

**Rules that make it work**

- **Name both systems and both owners.** A boundary with one signature is a preference.
- State the boundary **as a positive claim about each side**, not only as an exclusion. "A owns X"
  and "B owns Y" beats "A does not own Y."
- **Guardrails are the operative part**: what each side must not do to the other. Typically:
  neither writes into the other's directory; findings cross as proposals, never as edits; the
  owning side decides versioning (B1 / L-X7).
- A **scope note** records what the boundary deliberately does not settle. An unaddressed question
  named as unaddressed is honest; one left silent looks decided.
- It is versioned and ratified. An unratified draft is a proposal, and should say so.

```markdown
# <A> ↔ <B> boundary — governance record vX.Y.Z

## Ratified statement
<one paragraph: where authority divides, in positive terms for both sides>

## Roles
| System | Owner | Owns | Does not own |
|--------|-------|------|--------------|

## Guardrails
- <what each side must not do to the other>
- <how findings cross the boundary: proposal, not edit>
- <who decides versioning on each side>

## Scope note
<what this record deliberately does not settle, and what would reopen it>

**Ratified:** <date> by <both owners>
```

---

## Why these are documents and not ontology

Everything else in this package is machine-checkable. These three are not, and the distinction is
deliberate: each records a **judgement** — that a defect may wait, that an item is closed enough,
that a boundary falls here. A gate can verify that a findings register exists and is current; it
cannot verify that a deferral was wise.

That is the honest limit of the method. The gates carry what can be mechanised so that human
attention is spent on what cannot be — which is exactly the three decisions above.
