# Correction to oe-method v2.7.0 (commit 36b089a)

That commit message states the package was **"back into accordance with oe-pack v20.35.0."**
At the moment it was pushed the lineage gate reported `VERDICT: OUT OF ACCORDANCE — drift`
(one file, `testing_tbox_v1_4_0.ttl`) and the completeness gate exited 1. The release did not meet
its own definition of done, and the message asserted that it did.

**Cause.** The re-derivation ran a single pass over the gate's reported drift list. Re-deriving a
file changes the tree, so one pass is not a fixpoint — a file can enter the drift set after the
pass that was meant to clear it. Fixed by looping until the gate reports none.

**The deeper error is the same one this session has now made three times:** the claim was written
before the check was run, not after. L-65 and BP-D26 both govern it.

Corrected in v2.7.1. The v2.7.0 message stands unedited (L-112).
