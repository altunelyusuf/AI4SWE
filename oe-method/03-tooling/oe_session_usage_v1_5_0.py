#!/usr/bin/env python3
"""oe_session_usage_v1_5_0 - measure what a Claude Code session actually spent, raise a handover alarm,
record the measurement on the handover commit, and summarise recorded sessions by day or week.

Reads session transcripts (JSON Lines) and reports, from the recorded numbers only:
  - tokens by model and by class (fresh input, cache write, cache read, output)
  - turns, assistant messages, tool calls by tool, sub-agent launches
  - context size at the last message (what every further turn re-reads), per model
  - the largest tool results (bytes) - the usual cause of context growth
  - work done before the first file edit (the ceremony / orientation cost)

Counting rule (measured, not assumed): one assistant message is written to the transcript
as SEVERAL records (one per content block), each repeating the same usage numbers.
Usage is therefore counted ONCE PER MESSAGE ID. Summing every record overcounts.

Fail-closed rule: if no usage records are found, the tool refuses with exit 2 instead of
reporting zeros. It reports what it examined.

Coverage rule: long or compacted transcripts can hold assistant messages with no usage record.
Coverage = messages with usage / unique assistant messages. Below 100% every total is a LOWER BOUND:
the report is headed INCOMPLETE and the tool exits 3 (not 0). --allow-partial keeps the label but
returns 0. Context is reported per model, never across models.

New in v1.2.0 (OEE governance session, adopting v1.1.0 under the owner's delegation of 2026-10-05):
  --brief       one line: the handover alarm (OK / CONSIDER-HANDOVER / HANDOVER) and the figures behind it.
                Run at every turn's ceremony. The alarm reads the context re-read per turn of the model
                serving the latest measured message, because spend per turn tracks that figure (measured).
                Thresholds (v1.5.0, owner's ruling): consider at floor + 100,000, hand over at floor + 150,000,
                the floor being the session's own start; absolute 150,000 / 250,000 only when no floor is
                measured; override with --consider / --handover.
                The alarm is advisory: --brief always exits 0 unless the transcript is unreadable.
  --trailer     prints one `Session-Usage:` line to append to the commit a session makes at handover. The
                record rides an existing commit (no ledger file, no extra commits), the same channel the
                session register already reads for attribution (`Session:` trailers).
  --summarise   reads `Session-Usage:` trailers from git history (--repo-root) and prints spend per day or
                week (--by day|week, --since YYYY-MM-DD). A session's trailers are cumulative, so the
                summary counts each record's increase over that transcript's previous record, never the
                cumulative value again. Refuses (exit 2) when no trailer is found.

New in v1.3.0 (PROPOSED by the a product project session to the OEE governance session, 2026-10-05; scratchpad prototype):
  whole session  With no path, the newest transcript names the session; every transcript of that session under ANY
                working folder (~/.claude/projects/*/<id>.jsonl) and every sub-agent transcript
                (~/.claude/projects/*/<id>/subagents/*.jsonl) is read. v1.2.0 read the newest file only. --session
                does the same expansion for a path given. Sub-agents are reported apart; the alarm reads the main
                conversation only (a sub-agent's context is not the one each main turn re-reads).
  compactions   every compact_boundary record: trigger, tokens before and after (the harness's own preTokens /
                postTokens), and the FLOOR: the context of the first measured message after it (or of the
                session's first message). The brief line states the context as floor + growth.
  start-up      the floor split from measured numbers only: cached prefix (the first message's cache read: system
                prompt and tools), the compaction summary (postTokens), the rest (re-attached files, reminders).
  --simulate N  continue vs start fresh for the next N messages, from this transcript's own growth per message,
                reset base (context at the first file edit after each start) and summary size. --weights
                CR,CW,OUT (USD per million) prices it; without weights it prints token classes only.
  trailer v=2   adds floor, compactions and sub-agent totals; fresh/cache_write/cache_read/out are the WHOLE
                session (main + sub-agents). A v=1 and a v=2 record of one transcript are not differenced.

Authorship: v1.0.0 and v1.1.0 by the session-optimization-session; v1.2.0 by the OEE governance session;
v1.5.0 (OEE governance session): the alarm is judged against the session's own floor (owner's ruling 2026-10-05).
v1.4.0 (OEE governance session): --decide [--horizon N]. The alarm thresholds are a signal; the decision to hand over is made by
cost, prediction, risk, history and impact together, and holds only if it holds under the parameters a session cannot measure (price
weighting, reset base, growth). Tested by replaying one session's real history against fixed thresholds: fixed thresholds ranged from -38%
to +223% of the actual cost depending on those parameters, the scenario-robust rule from -30% to +6%.

v1.3.0 proposed by the a product project session.

Usage:
  oe_session_usage_v1_5_0.py [TRANSCRIPT.jsonl ...] [--session] [--json] [--top N] [--allow-partial]
  oe_session_usage_v1_5_0.py [TRANSCRIPT.jsonl ...] --brief | --trailer | --simulate N [--weights CR,CW,OUT]
  oe_session_usage_v1_5_0.py --summarise [--repo-root .] [--by day|week] [--since YYYY-MM-DD]
With no path it takes the newest transcript under ~/.claude/projects and every transcript of its session.
Several paths of the same session are merged and de-duplicated by message id.
"""
import argparse, datetime, glob, json, os, subprocess, sys
from collections import Counter, OrderedDict

KEYS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")
EDIT_TOOLS = {"Write", "Edit", "NotebookEdit"}
CONSIDER_DEFAULT = 150_000   # fallback ONLY when the floor is not measured (absolute), SESSION_OPTIMIZATION section 5
HANDOVER_DEFAULT = 250_000   # fallback ONLY when the floor is not measured (absolute), SESSION_OPTIMIZATION section 5
CONSIDER_ABOVE_FLOOR = 100_000   # owner's ruling 2026-10-05: judge the alarm against the session's own floor
HANDOVER_ABOVE_FLOOR = 150_000   # (floor = context of the first message after the start or the latest compaction)
TRAILER_KEY = "Session-Usage"


def session_files(seed):
    """Every transcript of the seed's session under any working folder, and its sub-agents' transcripts."""
    sid = os.path.basename(seed).rsplit(".", 1)[0]
    if os.path.basename(os.path.dirname(seed)) == "subagents":       # a sub-agent path names its session's folder
        sid = os.path.basename(os.path.dirname(os.path.dirname(seed)))
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(seed))))
    else:
        root = os.path.dirname(os.path.dirname(os.path.abspath(seed)))
    main = sorted(glob.glob(os.path.join(root, "*", sid + ".jsonl")))
    subs = sorted(glob.glob(os.path.join(root, "*", sid, "subagents", "*.jsonl")))
    return main, subs


def discover():
    paths = glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl"))
    return session_files(max(paths, key=os.path.getmtime)) if paths else ([], [])


def split_roles(paths):
    subs = [p for p in paths if os.path.basename(os.path.dirname(p)) == "subagents"]
    return [p for p in paths if p not in subs], subs


def block_bytes(content):
    if isinstance(content, str):
        return len(content.encode("utf-8", "replace"))
    if isinstance(content, list):
        return sum(block_bytes(b.get("text", b) if isinstance(b, dict) else b) for b in content)
    return len(str(content).encode("utf-8", "replace"))


def load(paths):
    records, bad = [], 0
    for p in paths:
        with open(p, errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line.startswith("{"):
                    continue
                try:
                    records.append(json.loads(line))
                except ValueError:
                    bad += 1
    return records, bad


def analyse(paths):
    records, bad = load(paths)
    msgs = OrderedDict()          # message id -> merged info (usage once per id)
    tool_names = {}               # tool_use id -> tool name
    tool_calls = Counter()
    results = []                  # (bytes, tool name)
    human_turns = 0
    first_edit_index = None
    seen_result_ids = set()
    seen_user_uuids = set()
    seen_tool_use = set()
    order = 0
    compactions = []              # one per compact_boundary record, in transcript order
    starts = [{"ts": None, "trigger": "start", "pre": None, "post": None}]   # the session start, then each compaction
    last_ctx = None

    for r in records:
        t = r.get("type")
        m = r.get("message") if isinstance(r.get("message"), dict) else {}
        if t == "system" and r.get("subtype") == "compact_boundary":
            md = r.get("compactMetadata") or {}
            ev = {"ts": r.get("timestamp"), "trigger": md.get("trigger"), "pre": md.get("preTokens"),
                  "post": md.get("postTokens"), "last_before": last_ctx}
            compactions.append(ev); starts.append(ev)
            continue
        if t == "assistant":
            mid = m.get("id") or r.get("uuid")
            info = msgs.setdefault(mid, {"model": m.get("model"), "usage": None, "order": order})
            u = m.get("usage")
            if isinstance(u, dict) and info["usage"] is None and m.get("model") != "<synthetic>":
                info["usage"] = {k: int(u.get(k) or 0) for k in KEYS}
                c = sum(info["usage"][k] for k in KEYS[:3])
                st = starts[-1]
                if "floor" not in st:
                    st.update(floor=c, prefix=info["usage"]["cache_read_input_tokens"], model=m.get("model"))
                st.setdefault("ctxs", []).append(c)
                last_ctx = c
            if m.get("model") and not info["model"]:
                info["model"] = m["model"]
            for b in m.get("content") or []:
                if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("id") not in seen_tool_use:
                    seen_tool_use.add(b.get("id"))
                    tool_names[b.get("id")] = b.get("name")
                    tool_calls[b.get("name")] += 1
                    if first_edit_index is None and b.get("name") in EDIT_TOOLS:
                        first_edit_index = len(msgs)
                    if b.get("name") in EDIT_TOOLS and "at_first_edit" not in starts[-1] and last_ctx is not None:
                        starts[-1]["at_first_edit"] = last_ctx
            order += 1
        elif t == "user":
            uid = r.get("uuid")
            if uid in seen_user_uuids:
                continue
            seen_user_uuids.add(uid)
            c = m.get("content")
            if isinstance(c, str):
                human_turns += 1
            elif isinstance(c, list):
                has_result = False
                for b in c:
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        has_result = True
                        tid = b.get("tool_use_id")
                        if tid in seen_result_ids:
                            continue
                        seen_result_ids.add(tid)
                        results.append((block_bytes(b.get("content")), tool_names.get(tid, "?")))
                if not has_result and any(isinstance(b, dict) and b.get("type") == "text" for b in c):
                    human_turns += 1

    msgs = OrderedDict((k, v) for k, v in msgs.items() if v["model"] != "<synthetic>" or v["usage"])
    with_usage = [(k, v) for k, v in msgs.items() if v["usage"]]
    latest_model = (with_usage[-1][1]["model"] or "unknown") if with_usage else None
    by_model = {}
    for _, v in with_usage:
        d = by_model.setdefault(v["model"] or "unknown", Counter())
        d["messages"] += 1
        for k in KEYS:
            d[k] += v["usage"][k]
    ctx = [sum(v["usage"][k] for k in KEYS[:3]) for _, v in with_usage]
    ctx_by_model = {}
    for _, v in with_usage:
        c = sum(v["usage"][k] for k in KEYS[:3])
        d = ctx_by_model.setdefault(v["model"] or "unknown", {"last": 0, "max": 0})
        d["last"] = c
        d["max"] = max(d["max"], c)
    total_msgs = len(msgs)
    coverage = (len(with_usage) / total_msgs) if total_msgs else 0.0
    before_edit = None
    if first_edit_index is not None:
        upto = set(list(msgs)[:first_edit_index])
        sub = [(k, v) for k, v in with_usage if k in upto]
        before_edit = {"messages": len(sub),
                       "cache_read_tokens": sum(v["usage"]["cache_read_input_tokens"] for _, v in sub),
                       "output_tokens": sum(v["usage"]["output_tokens"] for _, v in sub)}
    results.sort(reverse=True)
    measured_starts = [s for s in starts if "floor" in s]
    latest = measured_starts[-1] if measured_starts else None
    split = None
    if latest:
        summ = latest["post"] or 0
        split = {"floor": latest["floor"], "cached_prefix": latest["prefix"], "summary": summ,
                 "rest": latest["floor"] - latest["prefix"] - summ, "model": latest["model"], "after": latest["trigger"]}
    growth = [b - a for s in measured_starts for a, b in zip(s["ctxs"], s["ctxs"][1:])]
    return {
        "compactions": [{k: e.get(k) for k in ("ts", "trigger", "pre", "post", "last_before", "floor")} for e in compactions],
        "floors": [s["floor"] for s in measured_starts],
        "startup_split": split,
        "reset_base_samples": [s["at_first_edit"] for s in measured_starts if s.get("at_first_edit")],
        "growth_per_message_mean": round(sum(growth) / len(growth)) if growth else None,
        "summary_tokens": [e["post"] for e in compactions if e.get("post")],
        "examined": {"files": len(paths), "records": len(records), "unparseable_lines": bad,
                     "unique_assistant_messages": len(msgs), "messages_with_usage": len(with_usage),
                     "messages_without_usage": len(msgs) - len(with_usage),
                     "coverage": round(coverage, 4), "complete": len(with_usage) == len(msgs)},
        "human_turns": human_turns,
        "by_model": {k: dict(v) for k, v in by_model.items()},
        "totals": {k: sum(v[k] for v in by_model.values()) for k in KEYS},
        "tool_calls": dict(tool_calls.most_common()),
        "subagent_launches": tool_calls.get("Agent", 0),
        "context_tokens_last_message": ctx[-1] if ctx else 0,
        "context_tokens_max": max(ctx) if ctx else 0,
        "context_by_model": ctx_by_model,
        "latest_model": latest_model,
        "latest_message_measured": bool(msgs) and bool(list(msgs.values())[-1]["usage"]),
        "before_first_edit": before_edit,
        "largest_tool_results": [{"bytes": b, "tool": n} for b, n in results[:20]],
    }


def render(rep, top):
    e, t = rep["examined"], rep["totals"]
    out = []
    if not e["complete"]:
        out.append(f"*** INCOMPLETE: {e['messages_without_usage']} of {e['unique_assistant_messages']} assistant messages "
                   f"carry no usage record (coverage {e['coverage']:.1%}). Every total below is a LOWER BOUND. ***")
    out += [f"examined: {e['files']} main file(s), {e['records']} records, {e['unique_assistant_messages']} unique "
           f"assistant messages ({e['messages_with_usage']} with usage), {e['unparseable_lines']} unparseable lines",
           f"human turns: {rep['human_turns']}   sub-agent launches: {rep['subagent_launches']}",
           "tokens (each message counted once):"]
    for model, d in rep["by_model"].items():
        out.append(f"  {model}: {d['messages']} msgs | fresh in {d['input_tokens']:,} | cache write "
                   f"{d['cache_creation_input_tokens']:,} | cache read {d['cache_read_input_tokens']:,} | out {d['output_tokens']:,}")
    out.append(f"  TOTAL: fresh in {t['input_tokens']:,} | cache write {t['cache_creation_input_tokens']:,} | "
               f"cache read {t['cache_read_input_tokens']:,} | out {t['output_tokens']:,}")
    for model, c in rep["context_by_model"].items():
        out.append(f"context re-read per message, {model}: last {c['last']:,} | max {c['max']:,} tokens" + (" (last < max: compaction)" if c["last"] < c["max"] else ""))
    fl = rep["floors"]
    out.append(f"compactions: {len(rep['compactions'])}; floor (context of the first message after the start and each "
               f"compaction): latest {fl[-1]:,}, min {min(fl):,}, max {max(fl):,}" if fl else "compactions: 0; floor not measured")
    sp = rep["startup_split"]
    if sp:
        out.append(f"latest start ({sp['after']}), {sp['model']}: floor {sp['floor']:,} = cached prefix {sp['cached_prefix']:,} "
                   f"(system prompt and tools) + summary {sp['summary']:,} + rest {sp['rest']:,} (re-attached files, reminders, first prompt)")
    sub = rep.get("subagents")
    if sub:
        st = sub["totals"]
        out.append(f"sub-agents: {sub['files']} transcript(s), {sub['messages']} msgs | fresh in {st['input_tokens']:,} | cache write "
                   f"{st['cache_creation_input_tokens']:,} | cache read {st['cache_read_input_tokens']:,} | out {st['output_tokens']:,}"
                   + ("" if sub["complete"] else " (INCOMPLETE)"))
        wt = rep["whole_session_totals"]
        out.append(f"  WHOLE SESSION (main + sub-agents): fresh in {wt['input_tokens']:,} | cache write {wt['cache_creation_input_tokens']:,} "
                   f"| cache read {wt['cache_read_input_tokens']:,} | out {wt['output_tokens']:,}")
    b = rep["before_first_edit"]
    out.append("before first file edit: " + (f"{b['messages']} msgs, cache read {b['cache_read_tokens']:,}, out {b['output_tokens']:,}" if b else "no edit made"))
    out.append("tool calls: " + ", ".join(f"{k} {v}" for k, v in list(rep["tool_calls"].items())[:12]))
    out.append(f"largest tool results (top {top}): " + ", ".join(f"{r['tool']} {r['bytes']:,}B" for r in rep["largest_tool_results"][:top]))
    return "\n".join(out)


def thresholds(rep, consider=None, handover=None):
    """Effective thresholds. An explicit value wins; otherwise floor + 100,000 / floor + 150,000 when the floor
    is measured; otherwise the absolute fallbacks. Returns (consider, handover, basis)."""
    fl = rep["floors"][-1] if rep.get("floors") else None
    if fl is not None:
        c = consider if consider is not None else fl + CONSIDER_ABOVE_FLOOR
        h = handover if handover is not None else fl + HANDOVER_ABOVE_FLOOR
        basis = "floor-relative" if consider is None and handover is None else "explicit"
    else:
        c = consider if consider is not None else CONSIDER_DEFAULT
        h = handover if handover is not None else HANDOVER_DEFAULT
        basis = "absolute (floor not measured)" if consider is None and handover is None else "explicit"
    return c, h, basis


def alarm(rep, consider=None, handover=None):
    """Handover alarm from the context re-read per turn of the model serving the latest measured message."""
    consider, handover, _ = thresholds(rep, consider, handover)
    m = rep["latest_model"]
    ctx = rep["context_by_model"].get(m, {}).get("last", 0) if m else 0
    if not rep["latest_message_measured"]:
        status = "UNKNOWN"          # the newest message carries no usage: never guess the current size
    elif ctx >= handover:
        status = "HANDOVER"
    elif ctx >= consider:
        status = "CONSIDER-HANDOVER"
    else:
        status = "OK"
    return status, m, ctx


def _measures(rep):
    t = rep.get("whole_session_totals") or rep["totals"]
    return {"fresh": t["input_tokens"], "cache_write": t["cache_creation_input_tokens"],
            "cache_read": t["cache_read_input_tokens"], "out": t["output_tokens"]}


def brief_line(rep, consider, handover):
    status, m, ctx = alarm(rep, consider, handover)
    consider, handover, basis = thresholds(rep, consider, handover)
    e, x = rep["examined"], _measures(rep)
    fl = rep["floors"][-1] if rep["floors"] else None
    base = f" = floor {fl:,} + {ctx - fl:,}" if fl is not None else ""
    line = (f"USAGE {status}{' (run --decide)' if status in ('CONSIDER-HANDOVER', 'HANDOVER') else ''} | {m} context {ctx:,}{base} (consider {consider:,}, hand over {handover:,}; {basis}) | "
            f"compactions {len(rep['compactions'])} | turns {rep['human_turns']} | cache read {x['cache_read']:,} | "
            f"out {x['out']:,} | coverage {e['coverage']:.1%}")
    if rep.get("subagents"):
        line += f" | sub-agents {rep['subagents']['files']} file(s), cache read {rep['subagents']['totals']['cache_read_input_tokens']:,}"
    if not e["complete"]:
        line += " (INCOMPLETE: totals are lower bounds)"
    return line


def trailer_line(rep, paths, consider, handover):
    status, m, ctx = alarm(rep, consider, handover)
    session = "".join(c if c.isalnum() or c in "-_." else "_" for c in os.environ.get("OE_SESSION", "unattributed"))
    transcript = os.path.basename(paths[0]).rsplit(".", 1)[0][:12]
    x = _measures(rep)
    sub = rep.get("subagents") or {"files": 0, "totals": {"cache_read_input_tokens": 0}}
    fields = [("v", 2), ("session", session), ("transcript", transcript), ("model", m),
              ("turns", rep["human_turns"]), ("msgs", rep["examined"]["unique_assistant_messages"]),
              ("coverage", rep["examined"]["coverage"])] + list(x.items()) + [
              ("ctx", ctx), ("floor", rep["floors"][-1] if rep["floors"] else 0), ("compactions", len(rep["compactions"])),
              ("sub_files", sub["files"]), ("sub_cache_read", sub["totals"]["cache_read_input_tokens"]), ("status", status)]
    return f"{TRAILER_KEY}: " + " ".join(f"{k}={v}" for k, v in fields)


NUMERIC = ("fresh", "cache_write", "cache_read", "out")


def simulate(rep, n, weights=None):
    """Continue vs start fresh for the next n messages, from this transcript's own measurements only."""
    _, m, c = alarm(rep)
    g = rep["growth_per_message_mean"]
    bases = sorted(rep["reset_base_samples"]) or rep["floors"]
    summ = sorted(rep["summary_tokens"])
    if g is None or not bases:
        return "SIMULATE: not measured (needs at least two measured messages and one start); nothing printed as an estimate."
    b = bases[len(bases) // 2]
    s = summ[len(summ) // 2] if summ else None
    cont = {"cache_read": sum(c + g * k for k in range(1, n + 1)), "cache_write": g * n, "out": 0}
    fresh = {"cache_read": c + sum(b + g * k for k in range(1, n + 1)), "cache_write": b + g * n, "out": s or 0}
    lines = [f"SIMULATE next {n} messages from {m} context {c:,}; measured here: growth {g:,} per message, reset base "
             f"{b:,} (median context at the first file edit after a start, {len(rep['reset_base_samples'])} samples), "
             + (f"summary {s:,} (median of {len(summ)} compactions)" if s else "summary NOT MEASURED (no compaction): counted 0")]
    for name, d in (("continue", cont), ("fresh", fresh)):
        lines.append(f"  {name:<8} cache read {d['cache_read']:,} | cache write {d['cache_write']:,} | out {d['out']:,}")
    if weights:
        cr, cw, out = (w / 1e6 for w in weights)
        cost = lambda d: d["cache_read"] * cr + d["cache_write"] * cw + d["out"] * out
        lines.append(f"  priced at {weights} USD per million (cache read, cache write, output): continue {cost(cont):.2f}, fresh {cost(fresh):.2f}")
        be = next((k for k in range(1, 100000) if sum(c + g * i for i in range(1, k + 1)) * cr >
                   (c + sum(b + g * i for i in range(1, k + 1))) * cr + b * cw + (s or 0) * out), None)
        lines.append(f"  fresh is cheaper from {be} messages on" if be else "  fresh is not cheaper within 100,000 messages")
    else:
        lines.append("  not priced: pass --weights CR,CW,OUT (the account's prices are not visible to a session)")
    lines.append("  not modelled: rework after a handover beyond the measured reset base; the next work's own growth")
    return "\n".join(lines)


# ---- v1.4.0: the handover DECISION (advisory). A token count is a signal to run this, not the decision. ----
DEFAULT_HORIZON = 30
# Price weightings the account's real meter may follow. They are not visible to a session, so the decision
# must hold under both: reads-only (a quota that counts the re-read) and a write-heavy weighting.
# harness-fit is one session's least-squares fit of the harness's own cost records (USD per million: cache
# read, cache write, output) -- provisional, not the account meter.
PRICE_SCENARIOS = {"reads-only": (1.0, 0.0, 0.0), "harness-fit": (0.199, 4.027, 10.54)}
BREAKEVEN_CAP = 400


def _project(c, g, n, base, summ, point, w, fresh_now):
    """Priced cost of the next n messages from context c. fresh_now: hand over first (read c once, write the
    reset base, write the summary). The harness compacts by itself when the context reaches `point`
    (an uncontrolled reset to the same base)."""
    cost, ctx, events = 0.0, c, 0
    if fresh_now:
        cost += c * w[0] + base * w[1] + summ * w[2]; ctx = base; events += 1
    for _ in range(n):
        ctx += g
        if point and ctx >= point:
            cost += ctx * w[0] + base * w[1] + summ * w[2]; ctx = base; events += 1
        cost += ctx * w[0] + g * w[1]
    return cost, events


def _breakeven(c, g, base, summ, point, w):
    for n in range(1, BREAKEVEN_CAP + 1):
        if _project(c, g, n, base, summ, point, w, False)[0] > _project(c, g, n, base, summ, point, w, True)[0]:
            return n
    return None


def _scenarios(c, g, floor, bases, summ, point, n):
    """Grid over what a session cannot measure: price weighting, reset base, growth."""
    base_set = {"floor": floor, "median": sorted(bases)[len(bases) // 2] if bases else floor + 15000,
                "high": max(bases) if bases else floor + 40000}
    rows = []
    for wn, w in PRICE_SCENARIOS.items():
        for bn, b in base_set.items():
            for gn, gg in (("g/2", g * 0.5), ("g", g), ("1.5g", g * 1.5)):
                a, ea = _project(c, gg, n, b, summ, point, w, False)
                f, ef = _project(c, gg, n, b, summ, point, w, True)
                rows.append({"price": wn, "base": bn, "growth": gn, "continue_minus_fresh": a - f,
                             "breakeven": _breakeven(c, gg, b, summ, point, w), "compactions_continue": ea})
    return rows


def _verdict(rows, state_ok):
    pos = sum(1 for r in rows if r["continue_minus_fresh"] > 0)
    if not state_ok:
        return "FINISH-FIRST", pos
    if pos == len(rows):
        return "SWITCH", pos
    if pos == 0:
        return "STAY", pos
    return "STAY-UNLESS-LONG", pos


def git_state(root):
    """(uncommitted files, unpushed commits) of the working copy, or (None, None) when it cannot be measured."""
    def git(*a):
        r = subprocess.run(["git", "-C", root] + list(a), capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None
    st = git("status", "--porcelain")
    ahead = git("rev-list", "--count", "@{u}..HEAD")
    return (len(st.splitlines()) if st is not None else None), (int(ahead) if ahead and ahead.isdigit() else None)


def decide(rep, n, repo_root="."):
    _, m, c = alarm(rep)
    g = rep["growth_per_message_mean"]
    floor = rep["floors"][-1] if rep["floors"] else None
    if g is None or floor is None:
        return "DECIDE: not measured (needs at least two measured messages and one start); nothing printed as an estimate."
    bases = rep["reset_base_samples"]
    summ_l = sorted(rep["summary_tokens"]); summ = summ_l[len(summ_l) // 2] if summ_l else 0
    pre = [e["pre"] for e in rep["compactions"] if e.get("pre")]
    point = min(pre) if pre else None
    dirty, ahead = git_state(repo_root)
    state_ok = not ((dirty or 0) > 0 or (ahead or 0) > 0)
    rows = _scenarios(c, g, floor, bases, summ, point, n)
    verdict, pos = _verdict(rows, state_ok)
    bes = [r["breakeven"] if r["breakeven"] is not None else BREAKEVEN_CAP + 1 for r in rows]
    lo, hi = min(bes), max(bes)
    show = lambda b: f">{BREAKEVEN_CAP}" if b > BREAKEVEN_CAP else str(b)
    after = c + g * n
    out = [f"DECIDE continue or hand over -- advisory. The token count is the signal to run this, not the decision. ({m}, context {c:,}, floor {floor:,})",
           "1 STATE      : " + ("not measured (no git working copy at --repo-root)" if dirty is None else
                               f"{dirty} uncommitted file(s), {ahead if ahead is not None else 'unknown'} unpushed commit(s)" +
                               ("" if state_ok else " -> UNSAFE to switch: finish and push first")),
           f"2 COST       : next {n} messages, {len(rows)} scenarios (price weighting x reset base x growth): fresh is cheaper in {pos}, "
           f"continuing in {len(rows) - pos}; break-even between {show(lo)} and {show(hi)} messages",
           f"3 PREDICTION : growth {g:,.0f} per message -> context {after:,.0f} after {n}; reset base {sorted(bases)[len(bases)//2] if bases else floor:,} "
           f"({len(bases)} sample(s)), summary {summ:,}" + ("" if summ_l else " (NOT MEASURED, counted 0)"),
           "4 RISK       : " + (f"the harness compacted this session at {point:,}; at the current growth that is "
                               + (f"reached in about {max(0, int((point - c) / g))} messages (an automatic reset at a time not chosen, losing verbatim detail)" if g > 0 and c < point else "already passed")
                               if point else "no compaction observed in this session: its compaction point is NOT MEASURED")
                               + "; quality of a very long context and rework after a handover: NOT MEASURED (the trailer carries no rework count)"]
    try:
        recs = read_trailers(repo_root)
    except RuntimeError:
        recs = []
    if recs:
        ctxs = sorted(int(r.get("ctx", 0)) for r in recs if str(r.get("ctx", "0")).isdigit())
        out.append(f"5 HISTORY    : {len(recs)} Session-Usage record(s) in git; median final context {ctxs[len(ctxs)//2]:,}" if ctxs else f"5 HISTORY    : {len(recs)} record(s), no context field")
    else:
        out.append("5 HISTORY    : no Session-Usage records readable here: NOT MEASURED")
    out.append(f"6 IMPACT     : a handover re-reads {c:,} once and starts again at about {sorted(bases)[len(bases)//2] if bases else floor:,}; "
               "what the successor must be told is in the handover, what is only in this conversation is lost")
    why = {"FINISH-FIRST": "the working copy is not in a state to hand over",
           "SWITCH": "fresh is cheaper in every scenario, including the ones the session cannot measure",
           "STAY": "continuing is cheaper in every scenario",
           "STAY-UNLESS-LONG": f"the scenarios disagree: stay for work shorter than {show(lo)} messages; hand over at a clean boundary if the remaining work exceeds {show(hi)}"}[verdict]
    out.append(f"VERDICT      : {verdict} -- {why}")
    out.append("  not modelled: the next work's own growth; rework; the account meter (the two price weightings bracket it, they do not measure it)")
    return "\n".join(out)


def read_trailers(repo_root, since=None):
    cmd = ["git", "-C", repo_root, "log", "--all",
           f"--format=%H%x1f%cI%x1f%(trailers:key={TRAILER_KEY},valueonly,separator=%x1d)%x1e"]
    if since:
        cmd.insert(4, f"--since={since}")
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or "git log failed")
    recs = []
    for chunk in out.stdout.split("\x1e"):
        chunk = chunk.strip("\n")
        if not chunk:
            continue
        sha, when, values = (chunk.split("\x1f") + ["", ""])[:3]
        for v in values.split("\x1d"):
            v = v.strip()
            if not v:
                continue
            d = dict(kv.split("=", 1) for kv in v.split() if "=" in kv)
            ts = datetime.datetime.fromisoformat(when).astimezone(datetime.timezone.utc)
            rec = {"v": d.get("v", "1"), "commit": sha[:7], "time": ts, "session": d.get("session", "unattributed"),
                   "transcript": d.get("transcript", sha[:12]), "status": d.get("status", "?"),
                   "ctx": int(d.get("ctx", 0) or 0), "coverage": float(d.get("coverage", 0) or 0)}
            for k in NUMERIC:
                rec[k] = int(d.get(k, 0) or 0)
            recs.append(rec)
    return recs


def summarise(recs, by):
    """Each trailer is cumulative for its transcript: count the increase over the previous record."""
    recs = sorted(recs, key=lambda r: r["time"])
    prev, rows, restarts = {}, {}, 0
    for r in recs:
        p = prev.get(r["transcript"])
        if p and p.get("v") != r.get("v"):             # a v=1 record holds the main transcript only, v=2 the whole session
            p = None
        delta = {k: r[k] - (p[k] if p else 0) for k in NUMERIC}
        if any(v < 0 for v in delta.values()):     # not cumulative with its predecessor: count it whole
            delta, restarts = {k: r[k] for k in NUMERIC}, restarts + 1
        prev[r["transcript"]] = r
        if by == "day":
            key = r["time"].strftime("%Y-%m-%d")
        elif by == "week":
            y, w, _ = r["time"].isocalendar()
            key = f"{y}-W{w:02d}"
        else:
            key = r["session"]
        row = rows.setdefault(key, {"records": 0, "sessions": set(), "ctx_max": 0, "alarms": 0, "incomplete": 0,
                                    **{k: 0 for k in NUMERIC}})
        row["records"] += 1
        row["sessions"].add(r["session"])
        row["ctx_max"] = max(row["ctx_max"], r["ctx"])
        row["alarms"] += r["status"] in ("CONSIDER-HANDOVER", "HANDOVER")
        row["incomplete"] += r["coverage"] < 1.0
        for k in NUMERIC:
            row[k] += delta[k]
    for row in rows.values():
        row["sessions"] = len(row["sessions"])
    return rows, restarts


def render_summary(rows, by, restarts, n):
    out = [f"{TRAILER_KEY} summary by {by}: {n} record(s)" + (f", {restarts} not cumulative with their predecessor (counted whole)" if restarts else ""),
           f"{by:<22} sessions records   cache read   cache write        out   max context  alarms  incomplete"]
    for k in sorted(rows):
        r = rows[k]
        out.append(f"{k:<22} {r['sessions']:>8} {r['records']:>7} {r['cache_read']:>12,} {r['cache_write']:>13,} "
                   f"{r['out']:>10,} {r['ctx_max']:>13,} {r['alarms']:>7} {r['incomplete']:>11}")
    if any(r["incomplete"] for r in rows.values()):
        out.append("Rows with incomplete records are lower bounds.")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--allow-partial", action="store_true", help="print an INCOMPLETE report with exit 0")
    ap.add_argument("--brief", action="store_true", help="one line with the handover alarm (exit 0)")
    ap.add_argument("--trailer", action="store_true", help="print a Session-Usage: commit trailer line")
    ap.add_argument("--consider", type=int, default=None, help="absolute override; default floor + %d" % CONSIDER_ABOVE_FLOOR)
    ap.add_argument("--handover", type=int, default=None, help="absolute override; default floor + %d" % HANDOVER_ABOVE_FLOOR)
    ap.add_argument("--session", action="store_true", help="expand each path to every transcript of its session")
    ap.add_argument("--simulate", type=int, metavar="N", help="continue vs fresh for the next N messages")
    ap.add_argument("--decide", action="store_true", help="continue or hand over: cost, prediction, risk, history, impact (advisory)")
    ap.add_argument("--horizon", type=int, default=DEFAULT_HORIZON, help="messages of work still ahead (default %d)" % DEFAULT_HORIZON)
    ap.add_argument("--weights", help="CR,CW,OUT in USD per million, to price --simulate")
    ap.add_argument("--summarise", action="store_true", help="summarise Session-Usage trailers from git")
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--by", choices=("day", "week", "session"), default="day")
    ap.add_argument("--since")
    a = ap.parse_args(argv)
    if a.summarise:
        try:
            recs = read_trailers(a.repo_root, a.since)
        except RuntimeError as exc:
            print(f"REFUSED: {exc}", file=sys.stderr)
            return 2
        if not recs:
            print(f"REFUSED: examined the history of {a.repo_root} and found 0 {TRAILER_KEY} trailers. "
                  "An empty summary would be an absence of evidence presented as evidence.", file=sys.stderr)
            return 2
        rows, restarts = summarise(recs, a.by)
        print(json.dumps(rows, indent=2) if a.json else render_summary(rows, a.by, restarts, len(recs)))
        return 0
    if a.paths:
        main_p, sub_p = split_roles(a.paths)
        if a.session:
            ex = [session_files(p) for p in a.paths]
            main_p = sorted({p for mp, _ in ex for p in mp}); sub_p = sorted({p for _, sp in ex for p in sp})
    else:
        main_p, sub_p = discover()
    paths = main_p + sub_p
    if not paths:
        print("REFUSED: no transcript found (examined 0 files). Pass a path.", file=sys.stderr)
        return 2
    for p in paths:
        if not os.path.isfile(p):
            print(f"REFUSED: not a file: {p}", file=sys.stderr)
            return 2
    if not main_p:
        print("REFUSED: only sub-agent transcripts given; the alarm needs the main conversation.", file=sys.stderr)
        return 2
    rep = analyse(main_p)
    if sub_p:
        sr = analyse(sub_p)
        rep["subagents"] = {"files": len(sub_p), "messages": sr["examined"]["unique_assistant_messages"],
                            "complete": sr["examined"]["complete"], "by_model": sr["by_model"], "totals": sr["totals"]}
        rep["whole_session_totals"] = {k: rep["totals"][k] + sr["totals"][k] for k in KEYS}
        rep["examined"]["subagent_files"] = len(sub_p)
    rep["examined"]["main_files"] = len(main_p)
    if rep["examined"]["messages_with_usage"] == 0:
        print(f"REFUSED: examined {rep['examined']['records']} records but found 0 assistant messages with "
              "usage. A report of zeros would be an absence of evidence presented as evidence.", file=sys.stderr)
        return 2
    if a.brief:
        print(brief_line(rep, a.consider, a.handover))
        return 0
    if a.trailer:
        print(trailer_line(rep, main_p, a.consider, a.handover))
        return 0
    if a.decide:
        print(decide(rep, a.horizon, a.repo_root))
        return 0
    if a.simulate:
        w = [float(x) for x in a.weights.split(",")] if a.weights else None
        print(simulate(rep, a.simulate, w))
        return 0
    print(json.dumps(rep, indent=2) if a.json else render(rep, a.top))
    if not rep["examined"]["complete"] and not a.allow_partial:
        print(f"INCOMPLETE: coverage {rep['examined']['coverage']:.1%}; exit 3. Totals are lower bounds.", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
