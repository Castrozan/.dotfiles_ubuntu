### Repo ci tooling

Watch CI with `gh`: `gh run list --commit $(git rev-parse HEAD) --json databaseId,name,conclusion` gives the run ids for
a commit and `gh run watch <id> --exit-status` blocks on each until it finishes and exits non-zero when it ends red. A
short sha matches no run and a just-pushed commit has none for a few seconds, so pass the full sha and retry an empty
list rather than reading it as a verdict.

The integration and runtime tiers need the live machine, so a nightly 03:00 job owns them and no tick of yours ever runs
them; a red night is repo breakage you fix like a red CI. It reaches you as an inbox message from `nightly-deep-tiers`
carrying the verdict and the log path (`~/.local/state/dotfiles-nightly-tests/nightly-deep-test-tiers.log`). Read that
log, run the failing test files directly, fix and push when the cause is in the tree, and otherwise report the tier and
the failing test names to the human through notify. A passing night sends nothing.
