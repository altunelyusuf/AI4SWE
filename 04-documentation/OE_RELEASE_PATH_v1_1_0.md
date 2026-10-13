# The release path — one command, every check, in order (v1.1.0, 2026-10-07)

**Rule behind it:** BP-D55 and the run-length rules R1 to R9 of the discipline. **What it does not do:** it removes no check and loosens none; the publisher refuses everything it refused before. It removes the hand-work around them.

## 1. Build the stage, then run the path

A stage is a folder holding the package as it will be published: the new files, the old versions gone, `VERSION.txt` raised (BP-D7). Make it from a fresh `git pull` of the clone, never from memory of it.

```
export OE_SESSION=<your session name>        # GH_TOKEN must be set; it is passed on and never printed
python3 repo-tooling/oe_release_v*.py <stage> <package-slug>              # gates, manifest, dry-run
python3 repo-tooling/oe_release_v*.py <stage> <package-slug> --publish    # then publish, wait for CI and the tag
```

Run the first form as soon as the stage exists (R2), and again after each cluster of changes. Each step has a time limit and its duration is printed: checks 280 s, the publisher's dry-run and publish 1800 s because a package's own gate may legitimately take many minutes; `--step-timeout` overrides both. Before it starts, the tool prints the last measured durations for this stage and an expected total ("last time ... expect about N s"); say that figure before you wait (R8).

| Step | What it runs | If it refuses |
|---|---|---|
| gates | the stage's own `release_check` and `kb_integrity_guard`, when it ships them | fix the artifact; the output names the check |
| manifest | `oe_manifest`: bytecode and the publish record removed, the earlier manifest replaced (same naming form), the new one verified both ways | nothing to fix by hand; if it fails, a file changed after it was written |
| dry-run | the publisher with `--dry-run`: manifest, Turtle parse, structure check, discipline and governance source, deletion guard, version and tag checks, the record's shape | each refusal prints the command that clears it |
| publish | the real publisher, then `git pull`, the CI run of the new commit, and the release tag | a red CI run is a finding: read it, fix it in the next release |

The tag is made by the `OE tags` workflow after the push; a session cannot push a tag (HTTP 403, expected).

### Long gates (R9)

The publisher runs a package's own gates (`05-gates/*.py`, the release check) in the dry-run and used to run them again in the real publish. From repo-tooling 1.45.0 the dry-run writes a **receipt** (`<stage>.oe_gate_receipt.json`, beside the stage) and the real publish reuses it, printing "package gates: reused receipt". A receipt is valid only for the same bytes of the stage, the same upstream tree, the same head commit of the target repository, the same Python and an age of at most an hour; anything else runs the gates in full. `OE_FRESH_GATES=1` ignores it. The summary line says when it was reused.

Inside a package's own gate the same idea is available as `oe_gate_cache` (repo-tooling): `oe_gate_cache run --key-file <the checker script> --key-file <each data or rules file or folder> -- <command>` runs the command only when no passing run exists for the same command, the same bytes of every named file and the same Python. Only passes are stored; `OE_NO_GATE_CACHE=1` forces a run. The rule that keeps it sound: **name everything the step reads**, the checker included; a step that reads the network or the clock is not cached. A gate that validates the same files in several separate steps should run the validation once and share the result.

## 2. When it refuses

- **A deletion** (the guard found files at origin with no counterpart): the tool writes them to `<stage>.deletions.txt` and stops. Read the list. If every path is meant, rerun with `--expect-delete <that file>`; paths are relative to the package. Nothing is accepted for you, and `--force` accepts every deletion unseen.
- **The same refusal twice** (R3): the tool stops the third run (exit 3). Write what was wrong and what you changed, and rerun with `--cause "<text>"`. Do not run it a third time unchanged.
- **A time limit** (exit 4): find what the step waits on and fix that; do not run it again unchanged. A gate that is slow because it validates a lot is not a defect to hide: say its expected duration up front, and raise `--step-timeout` for that run.

## 3. Three orders that are not obvious

1. **A tool and the copy that must be byte-identical** (the module library and the class-table reader exist in repo-tooling and in the pack). Publish repo-tooling first, then the pack; CI is red on the first commit by construction (the identity gate sees one side). Say so in the plan before you publish (R6).
2. **A change of the class table.** The publisher reads the table from the governance clone, which is the previously published version, so its structure step does not see your new row. Check the stage against the new table yourself before you publish:
   `python3 repo-tooling/oe_structure_check_v*.py <root> --classes <new table> --register <aggregate>`. The same holds for the aggregate: it is read from the clone.
3. **The edition (the method).** Its vocabulary, lessons, discipline, documents and generic tools are authored in the edition itself, in general form; nothing about them is derived or copied from another package. Only the operating tools (ceremony, publisher, release path, manifest tools) are authored in repo-tooling because they run there; the edition lists them in `SHIPPED_TOOLS.txt` and `oe_release` refreshes them on the edition's stage (names replaced) before it checks anything. Publish repo-tooling first, then `oe_release` the edition; the mirror follows.

## 4. What stays by hand, and what to do about it

The plan amendment, the log rows and the next-session handover. If you do a step by hand a second time that is not in this list, build the tool before the third (R4).
