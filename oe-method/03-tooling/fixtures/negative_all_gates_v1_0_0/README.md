# Negative fixture: one small tree, three real gate failures

Consolidates what were three separate fixture directories (one per custom gate) into one,
following the same principle each one already proved individually — a gate never shown to fail
verifies nothing (`B3`/`L-95`) — without needing a separate tree per gate to prove it.

This tiny tree fails all three of `oe-method`'s own custom gates at once, each for a distinct,
real reason:

- **Lineage gate** — `LINEAGE.tsv` declares `orphan_tbox_v1_0_0.ttl` as derived from an upstream
  file that does not exist, so the gate correctly reports it `ORPHANED`.
- **Completeness gate** — that same file ships no matching ABox and claims no `BP-D51`
  exemption, so the pairing check correctly reports it `INCOMPLETE`. The entrypoint files below
  are deliberately minimal for the same reason (`GETTING_STARTED` under the required size,
  `LICENSE.md`/`VERSION.txt` absent).
- **Clean gate** — `plant.md` deliberately contains a real personal name outside any attribution
  exception, so the gate correctly reports `FAIL`.

See `NEGATIVE_FIXTURE_TRANSCRIPT.md` for the real, current output of all three.
