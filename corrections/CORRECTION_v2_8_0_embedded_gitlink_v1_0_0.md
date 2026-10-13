# Correction to oe-method v2.8.0 (commit 5b3db3f, tag oe-method-v2.8.0)

That publish reported every check passing — manifest 99/99, Turtle 58/58 parsed, package
gates all pass, ceremony conforms=True, violations=0 — and it was all true of the *source*
directory. It was not true of what actually reached GitHub: the published `oe-method/`
subfolder was **empty**. `cp -r` had copied the source's `.git` directory alongside the
real files; git recorded that as an embedded-repo GITLINK (tree mode 160000) rather than
tracked content, so the commit looked complete and contained nothing.

**Cause.** `oe_publish_v1_5_0.sh` had never been run against a SRC that was itself a git
clone before — every prior propagation session apparently built SRC fresh. Every check the
publisher ran was genuine and passed honestly; none of them inspects the pushed tree after
the fact, so the gap between "the source verifies" and "the destination has content" was
invisible to the tooling. `--dry-run` cannot close that gap either: it returns before the
clone-and-copy step runs at all.

**Caught by**: cloning the published repo fresh and checking `oe-method/` directly, rather
than trusting the publisher's own success output (BP-D2: never trust a summary, re-derive
from bytes — here, the "summary" was the tool's own passing verdict).

Fixed in repo-tooling v1.14.1 (`oe_publish_v1_5_1.sh`): `.git` is now excluded from the
copy. Corrected in oe-method v2.8.1. The v2.8.0 commit and tag stand unedited (L-112) —
history is not rewritten; this record and the superseding release are how the correction
is made visible.
