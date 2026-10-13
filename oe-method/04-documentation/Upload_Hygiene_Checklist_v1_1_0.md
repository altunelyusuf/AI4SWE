# Upload Hygiene Checklist v1.1.0

For claude.ai context-window economy.
Author: the method author · Issued: 2026-05-07 · Updated: 2026-05-13

---

## §1 Why this exists

Claude.ai's context window is **200,000 tokens** (Pro/Max plans) or 500,000 tokens (Enterprise). Files attached to a chat fall into two distinct handling regimes:

| Regime | What happens |
|---|---|
| **Auto-loaded text** (`.html`, `.md`, `.txt`, `.csv`) | Full file content is inserted into the context window the moment it is attached. Tokens are spent before the first message is processed. |
| **On-demand** (`.ttl`, `.json`, `.py`, `.pdf`, `.png`, `.zip`, all binaries) | Claude reads the file via tools (`view`, `bash_tool`, `unzip`, `rdflib`, etc.) only when needed. The bytes do not occupy context unless explicitly read. |

Token math (rule of thumb: ~4 characters per token for HTML/Markdown/Turkish prose):

| File size | Approx tokens | % of 200K window |
|---|---|---|
| 200 KB | ~50,000 | 25% |
| 400 KB | ~100,000 | 50% |
| 800 KB | ~200,000 | **100% — overflow** |
| 1.0 MB | ~250,000 | 125% — guaranteed overflow |

A single 963 KB HTML upload alone exceeds the entire context window. This is why "conversation too long" can fire on the very first message.

---

## §2 Pre-upload checklist (user side)

### §2.1 Auto-load table

| Format | Auto-loads to context? | Action for files > 200 KB |
|---|---|---|
| `.html` | **YES** | Wrap in `.zip` |
| `.md`   | **YES** | Wrap in `.zip` |
| `.txt`  | **YES** | Wrap in `.zip` |
| `.csv`  | **YES** | Wrap in `.zip` |
| `.ttl`  | no  | Attach directly |
| `.owl`  | no  | Attach directly |
| `.json` | no  | Attach directly |
| `.py` / `.js` / `.jsx` | no | Attach directly |
| `.pdf`  | no (rasterised on demand) | Attach directly |
| `.png` / `.jpg` | no (image input) | Attach directly |
| `.zip` / `.tar.gz` | no (binary) | Attach directly |
| `.docx` / `.xlsx` / `.pptx` | no (binary) | Attach directly |

### §2.2 Hard rules

1. If a single text-format file's content exceeds 200 KB, zip it.
2. Do **not** attach the same file both loose AND inside a zip — the loose copy still auto-loads. Attach only the zip.
3. Stable governance artifacts (a reliability ontology, META, OQC, CORE, AMOD shape sets, OE Pack manifests) belong in the **Project knowledge base** (RAG-retrieved on demand, not auto-loaded).
4. Per-session ad-hoc artifacts (workbench iterations, PPTX builds, GPPT generators) attach as zips per the table above.
5. Disable connectors (Drive/Gmail/Calendar/web search/research) you do not need for the current task — each one's tool schema costs additional context.

### §2.3 Quick zip command

```bash
# Pre-upload one-liner
zip -j artifact_bundle_$(date +%Y%m%d_%H%M).zip *.html *.md
```

---

## §3 Per-session checklist (Claude side)

To be observed at the top of every working session.

| Step | Action |
|---|---|
| C-1 | `ls -la /mnt/user-data/uploads/` — inventory all uploaded files with byte sizes. |
| C-2 | For any uploaded `.html`/`.md`/`.txt`/`.csv` > 200 KB found loose, surface a **context-cost warning** with token estimate. |
| C-3 | Recognise that loose text uploads are already in context — do not re-read with `cat`/`view`; reference directly. |
| C-4 | For zipped uploads, extract to `/home/claude/`, then inspect slices via `grep`, `sed -n '<start>,<end>p'`, or `view` with `view_range`. Avoid full-file `cat` on anything > 200 KB. |
| C-5 | For TTL/OWL ontologies, prefer programmatic queries (`rdflib`, `pyshacl`, SPARQL) over text grep when the question is structural. |
| C-6 | If cumulative loose text uploads exceed 100 KB, recommend the user re-upload as a zip in a fresh session before proceeding. |

---

## §4 Response economy (Claude side)

Beyond upload hygiene, response-side economy also affects context cost and user attention. The following rules apply throughout each working session.

### §4.1 Simple narrative as default

| Step | Action |
|---|---|
| R-1 | **Answer in simple narrative by default.** Provide explanations as concise prose, not as multi-section deliverables, unless the user explicitly requests structured output. |
| R-2 | **Details only when asked.** Do not pre-emptively elaborate substructures, bullet enumerations, tables, or step-by-step breakdowns unless the user requests them or the task is explicitly structural (e.g., audit reports, work-package plans). |
| R-3 | **One direct answer first; offer to expand.** If multiple dimensions of detail are available, answer the direct question first in 2-5 sentences, then offer "I can detail X, Y, or Z if useful" — let the user pull more depth. |
| R-4 | **No proactive option menus on settled questions.** If the user has already ruled on a matter (naming, structure, scope), do not re-open it with "you could also consider..." framings. This is `FalseDichotomyDrift` prevention; the rule is operationalized by `ContradictionSurfacingProtocol`. |
| R-5 | **No filler hedges on settled rules.** Phrases like "would benefit from", "is also defensible", "weakly held", "could stay X-form" are reserved for genuinely open empirical questions, not for re-opening binding decisions. |

### §4.2 When structured output IS appropriate

The default is simple narrative, but structured output (tables, multi-section docs, bullet hierarchies) is appropriate when:

- The user explicitly requests it ("give me a table of...", "list the findings", "audit and report")
- The deliverable is a formal artifact by nature (audit document, work-package plan, ontology authoring spec)
- The content is genuinely enumerative (a list of 15 BP-D7 mismatches IS a list)

The discriminator: **does the structure serve the user, or does it pad the response?** If padding, use prose.

---

## §5 Standing prompt addition

Append the following to the standard task-prompt block:

```
Upload hygiene. Deliver .html/.md/.txt/.csv artifacts >200 KB inside a .zip;
do not attach them loose alongside the zip. (These four formats auto-load
as text into the context window and consume tokens before the first message
is processed; .ttl/.json/.py/binary types do not.) On receipt, inventory
uploaded file sizes and estimate context cost before reading; read slices
with grep/sed/view_range, not full cat. Stable governance artifacts
(a reliability ontology/META/OQC/CORE/AMOD) belong in the Project knowledge base.

Response economy. Answer in simple narrative; provide details only when
asked. One direct answer first; offer to expand if multiple dimensions
are available. No proactive option menus on settled questions. No filler
hedges ("would benefit from", "is also defensible", "weakly held") on
settled rules — reserved for genuinely open empirical questions.
```

---

## §6 Project knowledge base discipline

Files that are stable across many sessions should live in a Claude Project's knowledge base (RAG-retrieved, not auto-loaded):

- a reliability ontology / META / OQC / CORE / AMOD ontologies and shape sets
- OE Pack version manifests, verifier scripts, README files
- Course content blueprints (CCGS, COM0463, COM4061, SEN4012)
- Standing skill files (a reliability ontology safeguard documents, RoboLearn templates)
- an algebraic framework Phase artifacts (ontology, executor, quality emitters)

Working artifacts — workbench iterations, GPPT generators, course HTML pages, PPTX builds — remain per-chat uploads using the §2 zip rules.

---

## §7 Self-test before sending a prompt

Four questions to ask before clicking Send:

1. Are any loose `.html`/`.md`/`.txt`/`.csv` attachments larger than 200 KB? If yes → zip first.
2. Is the same file attached both loose and inside a zip? If yes → remove the loose copy.
3. Is the artifact stable across sessions (governance / safeguard / blueprint)? If yes → move it to the Project knowledge base instead.
4. Does the task-prompt include the response-economy rule (§5)? If a concise narrative answer is wanted, including the rule prevents over-elaboration.

---

## §8 Version & lineage

| Field | Value |
|---|---|
| Document | `upload_hygiene_checklist_v1_1_0.md` |
| Version | 1.1.0 |
| Issued | 2026-05-07 |
| Updated | 2026-05-13 |
| Lineage | **CONTINUATION** MINOR bump from v1.0.0 — adds §4 Response economy + §5 prompt amendment + §7 fourth self-test question. No breaking changes to v1.0.0 rules; all original sections (§1–§3, prior §4 prompt template, §5 KB discipline, §6 self-test) retained as §1–§3, §5, §6, §7 in this version. |
| Scope | claude.ai web/mobile/desktop chat surface |
| Out of scope | Claude Code CLI (different context handling), API direct usage |
| Companion artifact | Standing prompt template (see §5) |
