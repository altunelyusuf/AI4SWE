# Session optimization — v1.4.1

**Status: adopted into `repo-tooling` v1.18.0 by the OEE governance session, 2026-10-05, under the
owner's explicit delegation ("take the control of the task, process the request and build an optimum
solution to use as a part of OEE ecosystem").** The four rulings the proposal asked for, and the two
added later, were decided under that delegation; each decision and its reason is in section 8. The
thresholds and the model-fit table remain stipulations: they are advisory, nothing refuses work on
them, and they are recalibrated from recorded measurements (section 5). Every number below was
measured in the session that wrote it, on the date given, and says how. Anything not measured is
labelled *unverified*. Changes are listed at the end.

Sections 1–4, 6 and 7 written 2026-10-04/05 by the `session-optimization-session` (v1.0.0, v1.1.0);
sections 5 and 8 and the status rewritten by the OEE governance session (v1.2.0). Ontology-based sessions across the OEE
ecosystem can use it to see where their tokens go and to pick a fitting model, without guessing.

---

## 1. What a session can measure about itself

A Claude Code session writes a transcript, one JSON record per line, at
`~/.claude/projects/<working-folder-slug>/<session-id>.jsonl`. Each assistant record carries the
model name and exact token usage: fresh input, cache write, cache read, output. So a session need
not estimate its own cost — **where those records exist.** Long sessions that were continued after
their history was compacted can hold assistant messages with no usage record (the governance
review measured 1,218 of 1,245 assistant records without one; this session: 3 of 60 messages).
The tool states its coverage and never presents a partial total as a whole one. (Observed on this container, 2026-10-04. *Unverified* for chat
sessions on claude.ai, which keep their record elsewhere; there the turn count from the chat record
is the only available measure.)

**The counting rule that matters.** One assistant message is written as several records, one per
content block (thinking, text, each tool call), and every one repeats the same usage numbers.
Measured on this session's own transcript: 93 records came from 27 messages, and adding every
record gave 15.0 million cache-read tokens against 4.13 million counted once — an overcount of
about 3.6 times. The governance session measured 2.5 times on its own transcript, so the factor
depends on the transcript; it is not a constant. The tool counts each message once.

**The tool.** `oe_session_usage_v1_5_0.py` (v1.1.0 when this section was written) prints tokens by model, human turns, tool calls by tool,
sub-agent launches, the context size re-read on every message (per model, last and max; last below max is normal
after compaction), the largest tool results, and the work
done before the first file edit. It refuses (exit 2) instead of printing zeros when it finds no
usage records, following the bootstrap's rule that an empty examination must fail. When some
messages have usage and some do not, it heads the report INCOMPLETE, says every total is a lower
bound, and exits 3 (`--allow-partial` keeps the label and exits 0). Its test shows a known
transcript passing and the bad inputs refused, and ships three mutations that must fail: a
per-record counter (fails 8 checks, measured), coverage forced complete (1 check), and exit 3
replaced by 0 (the exit-code check).

## 2. Where the tokens go — measured here, to be re-measured elsewhere

On this session's transcripts (two working folders merged, 2026-10-04 21:20, 29 messages with usage):

| Measure | Value |
|---|---|
| Cache read (history re-read each turn) | 5,073,326 tokens |
| Cache write (new material added to history) | 268,954 tokens |
| Output (what the model wrote) | 35,129 tokens |
| Fresh input | 58 tokens |
| Context re-read per turn, now | 243,078 tokens |
| Work before the first file edit | all 29 messages |

Reading: nearly all spend is the history being re-read, and the history grows with every turn.
Output is under one percent of the total. The largest additions to the history were one chat-list
result (44,923 bytes) and one discipline file read whole (38,466 bytes). Cost per turn therefore
tracks the size of the history, not the size of the answer. *Unverified:* how cache reads weigh
against a weekly limit; confirm on the account's usage page before converting tokens to a limit.

Consequences that follow from the measurement, not from taste:

1. A long session is expensive because of its length, whatever it is doing.
2. The first turns of a governed session are orientation (fetch, hash, extract). That cost is paid
   once and then re-read on every later turn, so keep it small: read headings and the sections
   needed, never a whole large file (the discipline already says slices, never a full read above
   200 KB).
3. Large tool results are the usual cause of growth. The report lists the top five.

## 3. The request to give any session

Paste this into a session to get the same answer from every one. Each figure must come from a
command run in that turn, not from recollection.

```
SESSION OPTIMIZATION REPORT — run `python3 "$(ls repo-tooling/oe_session_usage_v*.py | sort -V | tail -1)"` now (highest
version; if the report is headed INCOMPLETE, say so and give the coverage), then answer from its output only:
 1. Models used and tokens per model, by class (fresh, cache write, cache read, output).
 2. Human turns, and the context re-read per turn now.
 3. The three largest tool results, and whether any file over 200 KB was read whole.
 4. Work before the first file edit (orientation cost) as a share of the total.
 5. Rework: list each place this session corrected its own earlier output (a re-issued version, a
    reverted change, a claim withdrawn) with the commit or file as evidence; count only evidenced ones.
 6. For the work still ahead: which kind of work it is (Section 4), the model that fits, and whether
    to continue here or hand over and start fresh, with the reason.
Say plainly which items you could not measure. Do not fill a gap with an estimate.
```

## 4. Model fit by kind of work — adopted as advisory guidance

This table is a stipulation: the honest answer to "why this and not the other" is judgement plus
the rework record of the week it was drawn from, not a rule. Adopted under the owner's delegation as
**advisory guidance**: a session uses it to say which tier fits the work ahead (item 6 of the request
above); nothing checks or enforces it. Revisit it when the recorded summaries (section 8) show rework
or spend by kind of work.
Model names are as of 2026-10-04 and go stale; the tier is what matters. The cost order
(smaller tier cheaper) is general expectation, *unverified* against the account's own meter.

| Kind of work | Fits | Why | Rework risk if downgraded |
|---|---|---|---|
| Writing or changing governance rules, shapes, or the discipline itself | Highest-capability general tier (Opus 5.5) | Errors propagate to every package; the week's records show repeated shortcuts caught only by the owner | High |
| Design decisions that are stipulations (grammar, notation, taxonomy) | Same | A wrong choice is built upon before it is noticed | High |
| Building a package under a lineage (stages, witnesses, gates) | Same, hand to the middle tier for mechanical steps | Skipped ceremony steps were the recurring failure | High |
| Running a fixed, tested pipeline (page builds, test runs, manifest rebuilds) | Middle tier (Sonnet 5.5) | The pipeline's own checks catch errors | Low |
| Parallel workers on the same fixed pipeline | Middle tier, cap how many run at once | Each worker carries its own growing history | Low |
| Handover or inbox sweeps, release steps from a script | Middle tier | Procedure is written down | Low to medium |
| A deterministic action with a script (pushing a tag from a local machine) | No model | Zero tokens, nothing to get wrong | None |
| Finding a chat or file | Smallest tier (Haiku 4.5) | Lookup | Negligible |

The Fable 5.1 tier, the most capable and presumably the most costly, is for the hardest first-time
design rounds if at all; no measurement here supports routine use.

## 5. When to hand over — a provisional alarm, recalibrated from records

**What the alarm reads.** The context re-read per turn by the model serving the latest measured
message. That is the figure the measurement in section 2 ties spend to: every turn re-reads the whole
history, so a turn costs roughly what the history weighs, whatever the turn does. Turn counts are a
weaker proxy (a turn that reads one large file weighs more than ten small ones).

**Thresholds (owner's ruling, 2026-10-05: judge the alarm against the session's own floor).** The floor is the context of the session's first message after its start or after a compaction (the system prompt, the tools, the summary and what is re-attached). Measured floors differ between sessions (72,680; 104,273; 108,696; 117,033), so an absolute number sits at a different distance from the start in each.

| Context re-read per turn | Alarm | Meaning |
|---|---|---|
| below floor + 100,000 | `OK` | carry on |
| floor + 100,000 to floor + 149,999 | `CONSIDER-HANDOVER` | run `--decide`; finish the current unit of work, then hand over if it says so |
| floor + 150,000 and above | `HANDOVER` | run `--decide`; hand over at the next clean stopping point unless it says STAY |
| newest message has no usage record | `UNKNOWN` | never guessed; say so |
| floor not measured | the old absolute 150,000 / 250,000 | a fallback only, and the line says so |

Why these and not others, honestly: one session's backtest (a parallel session's proposal) found the lowest weighted cost near an absolute 250,000, flat between 200,000 and 300,000, and worse at 150,000 than doing nothing; expressed against that session's floor of about 137,000 that is roughly floor + 100,000 to + 150,000. Beyond that single case no measurement decides the numbers, so they stay provisional and the ten-record calibration below applies. The first, absolute numbers were chosen so that
the governance session writing this (at 227,814 when the alarm was first run) would have been told to
consider a handover well before the end of its work, and so that ordinary sessions after a ceremony
read stay below the first mark. The alarm is advisory: `--brief` always exits 0 when it can measure.

**Calibration (how the numbers stop being judgement).** Every session records a `Session-Usage:`
trailer on its handover commit (section 8). After ten recorded handovers, the governance session runs
`--summarise --by session`, compares the alarm level each session reached with its rework (item 5 of
the request above), and proposes revised thresholds to the owner. The offsets live in the tool as
two named constants (`CONSIDER_ABOVE_FLOOR`, `HANDOVER_ABOVE_FLOOR`) and change only with a new tool version.

## 6. Uploads: zip or flat files

**Measured:** the zip attached to this session arrived as a path only. Its contents were not in the
conversation until a command extracted them and the file was read, so a zip adds nothing to the
history until it is opened. **Not measured:** how a flat text file attached directly is handled; the
harness is described as often showing text attachments in the conversation, which would add them to
the history on every turn. Test it once: attach one flat file, run the tool before and after, and
compare cache write.

What matters more is the file's bytes. The attached `BOOTSTRAP_v1_3_0.md` carried 93 backslashes,
49 of them escaped underscores (`OE\_SESSION`), and a token line with triple-escaped characters that
a command would not read. The escaping was inside the file; zipping did not cause it and flat
attachment would not have removed it. The current bootstrap has 8 backslashes. Checking the bytes
after unpacking is the safeguard, whatever the wrapper.

| Question | Zip | Flat file |
|---|---|---|
| Adds to history before it is read | No (measured) | Possibly (unverified) |
| Keeps folder layout of a package | Yes | No, paths are lost |
| Several files in one upload | Yes | One at a time |
| Digest | Verify the inner files after extracting; the wrapper's own digest changes with timestamps | The file's digest is the file's identity |
| Best for | Packages, anything over 200 KB, anything with a manifest | A single small file wanted in view at once |

Rule of thumb, matching the existing upload-hygiene line in the discipline: ship large or
multi-file material as a zip, verify the inner manifest, and read slices.

## 7. What this does not cover

- No weekly-limit percentages: the account meter is not visible to a session.
- Chat sessions on claude.ai: transcripts were not reachable from this container.
- Sessions whose usage records are missing for part of their life: the tool reports the coverage and
  stops there. Totals for those sessions are lower bounds; the turn count from the chat record is
  the fallback measure.
- Sub-agent usage is counted only if the transcript records it as part of the session; none was
  launched in the measured session, so that path is untested.
- Token cost of the governed ceremony per package: needs the report from each package's own session.

## 8. The meter, the record and the summaries — decided 2026-10-05

| Need the owner named | Built | Not built, and why |
|---|---|---|
| An alarm telling a session when to switch | `--brief`: one line with `OK` / `CONSIDER-HANDOVER` / `HANDOVER`, run as part of every turn's ceremony (bootstrap step 1). Zero model work: it is a command, and its output is one line, so it barely adds to the history it measures. | A settings hook or a plugin toast (alternatives A and C of the proposal): how they load in a session and what a hook's output reaches is *unverified*, and loading them raises the person's consent prompt, which nothing should answer for them. The ceremony line gives the same alarm with no installation. |
| A per-session record | `--trailer`: one `Session-Usage:` line appended to the commit the session already makes at handover. No ledger file and no extra commits. The session register already reads attribution from commit trailers (`Session:`), so this follows the existing pattern instead of opening a second channel (consolidate before creating). | A ledger file: every write would be a commit of its own, and parallel sessions would conflict on one file. |
| Daily and weekly summaries | `--summarise --by day|week|session [--since YYYY-MM-DD]`, read straight from git history. Trailers are cumulative per transcript; the summary counts each record's increase over that transcript's previous record, so a session that hands over twice is not counted twice. Refuses when it finds no trailer. | A scheduled daily task: each firing is a fresh session that spends tokens to report on tokens, and it cannot read live transcripts anyway; the summary is a deterministic command any session (or the owner) runs in seconds. |
| Placement | Tool, test, fixtures and this document in `repo-tooling`; the tool, this document and the bootstrap derived into `oe-method` through the usual pipeline, from which the mirror follows. | — |
| The bootstrap change | Bootstrap v1.6.0: the proposal's measuring step and upload rule, plus the per-turn alarm line and the trailer at handover. | — |

**Limits stated, not hidden.** The record covers only sessions that run the bootstrap and commit at
handover. Totals are lower bounds wherever coverage is below 100% (the trailer carries the coverage,
and the summary counts incomplete records). An outlier message within one model is not filtered from
the context figure. Weekly-limit percentages remain invisible to a session (section 7).

## 9. The handover decision — a method, not a token count (v1.3.0)

**Why.** A threshold on the context size decides on one number. Replaying one session's real history (152 messages,
one compaction) against several fixed thresholds, with the two bounds of what the account may charge for, gave results
from 38 % below to 223 % above the cost of doing nothing, depending on two parameters a session cannot measure: how the
account weights cache reads against cache writes, and how large the context is after a fresh start. A rule that gives
opposite answers for parameters nobody can read is not a decision rule.

**What.** `oe_session_usage_v1_5_0.py --decide --horizon N` weighs six factors, each printed with whether it was
measured: (1) state: uncommitted files or unpushed commits make a handover unsafe, so the answer is FINISH-FIRST;
(2) cost: the next N messages priced for continuing and for starting fresh, over a grid of price weighting x reset base x
growth, with the break-even in messages; (3) prediction: the growth per message, the context after N, the summary size;
(4) risk: the point where the harness compacted this session by itself (an uncontrolled reset that loses verbatim detail,
L-85) and how many messages away it is; quality of a very long context and rework after a handover are not measured and say
so; (5) history: the Session-Usage records in git; (6) impact: what a handover re-reads and what the successor must be told.

**Verdict.** SWITCH only if fresh is cheaper in **every** scenario; STAY only if continuing is cheaper in every scenario;
otherwise STAY-UNLESS-LONG with the break-even range, so the choice depends on the work still ahead, which is the one thing
the person knows. It is advisory: the thresholds in section 5 are the signal to run it.

**Test drive.** Replayed on that session at its turn boundaries, six combinations of price weighting and reset base:
the scenario-robust rule cost between 69.6 % and 106.2 % of the actual cost; the fixed thresholds between 61.6 % and
323 %. Its worst case is far smaller; it is not always the cheapest (a threshold that happens to match the unknowns wins).
**Limits:** one session and one compaction; the cost is the harness's list estimate, not the account meter; a compaction is
modelled as costing the same as a handover; nothing here measures quality loss or rework, which is why the verdict is advisory.
Re-run it on more records before treating the break-even as settled; the tool's 71 checks and ten mutations prove the arithmetic
and the rule, not the prices.

## Changes from v1.4.0 (v1.4.1, PATCH)

- A note appended to the v1.4.0 entry below, which is left as written (a history is corrected by a note, not rewritten): the ceremony's read of the discipline is now `oe_ceremony_digest_v1_1_0.py`, no longer the first version named there. Nothing else changed.

## Changes from v1.3.0 (v1.4.0, MINOR)

- Section 5: the alarm is judged against the session's own floor (consider at floor + 100,000, hand over at floor + 150,000), the owner's ruling of 2026-10-05; the absolute numbers remain only as a fallback when no floor is measured. Tool v1.5.0.
- The ceremony reads the discipline through `oe_ceremony_digest_v1_0_0.py` (rule sections in full, change history as headings, a rules check that fails on a discipline whose rules still sit only in the history). Possible because discipline v2.13.0 / v2.13.1 moved the two history-only rules into the rule sections. About 35 % fewer bytes (25,721 of 39,069 on v2.13.1); the token saving is a parallel session's measurement, not repeated here.

## Changes from v1.2.1 (v1.3.0, MINOR)

- Section 9 new: the handover decision. Tool v1.4.0 adds `--decide` and `--horizon`; the brief line points at it when the alarm is CONSIDER-HANDOVER or HANDOVER. Thresholds unchanged.

## Changes from v1.2.0 (v1.2.1, PATCH)

- The tool is now v1.3.0 (adopted from a session's worked copy after the OEE session re-derived it: 56 of 56 checks, and run on a real split session). It reads the **whole session**: with no path it takes the newest transcript's session id and reads that id's file in every working folder plus its sub-agent transcripts, reported apart (the alarm reads the main conversation only). v1.2.0 read one file and undercounted a session whose transcript was split by a working-directory change (79 of 83 messages here) or that launched sub-agents (20 % in another session).
- The report lists **compactions** and the **floor** (the context of the first message after a start or a compaction), and `--brief` states the context as floor + growth. The trailer is `v=2` and carries floor, compactions and sub-agent totals; `--summarise` never differences a `v=2` record against a `v=1` one.
- `--simulate N` answers "continue here or start fresh for the next N messages" from the session's own numbers.
- **Unchanged:** the alarm thresholds (150,000 and 250,000, absolute) and their recalibration after ten recorded handovers. Judging the alarm against the session's own floor is a proposed change, not adopted: the floors measured so far differ between sessions (72,680; 108,696; 117,033), which is the evidence for it, and it is pending the owner's ruling.

## Changes from v1.1.0

- Status: adopted (v1.2.0) under the owner's delegation; rulings recorded in sections 4, 5 and 8.
- Section 5: provisional alarm thresholds with their reason and a calibration rule, replacing "no number proposed".
- Section 8 new: the meter (`--brief`), the record (`--trailer`), the summaries (`--summarise`).
- The request block resolves the tool by highest version explicitly.

## Changes from v1.0.0

- Tool reference v1.0.0 → v1.1.0; coverage rule, per-model context, shipped mutations.
- The "seven checks" figure is withdrawn; the shipped test measures 8 for the per-record counter.
- The 3.6× overcount is stated as transcript-dependent (2.5× on the governance session's own).
- "Each assistant record carries usage" is qualified for long and compacted sessions.
