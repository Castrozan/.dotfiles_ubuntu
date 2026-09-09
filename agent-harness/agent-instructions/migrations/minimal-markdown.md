### Goal and launch boundary

Migrate dotfiles-owned AI instructions from XML sections to minimal Markdown, preserve their prose and behavior, and
make deterministic tests reject every document outside the accepted format. Deploy the result through the existing Nix
owners across Claude Code, Codex, OpenCode, Pi, and Hermes wherever each supports the surface. This is the canonical
implementation tracker. The human launched the goal; milestone 2 is in progress. Update this tracker when evidence
changes the plan and remove stale claims.

### Starting evidence

Investigation started at public revision `1b594e0c5c72d53fd4d1befbc7f8f9cb5da193cb`. The existing scanner found 97
instruction files: 78 public and 19 private, containing 636 standalone opening XML sections and 59 inline XML section
references. These are an observed inventory, not fixed acceptance counts. Three focused format, structure, and prose
test files passed all 29 tests before implementation. Inspect current revisions, sibling worktrees, private submodule
state, and peer work before each increment.

### Scope and preserved behavior

Cover core rules, project context, rebuild guidance, skills and their instruction references, subagent definitions,
owned runtime prompts, source-search instructions, and generated instruction fragments. Derive discovery from the
existing scanner and actual Nix consumers, including private shared skills and machine skills. Validate public-only CI
and a checkout with the private submodule. Keep private contents and provenance in their private repository.

Preserve authority placement, discovery metadata, skill names, routing, workflow order, approvals, permissions, refusal
conditions, model selection, interactive reply shape, and baseline gates. This changes authoring representation only.
Keep AGENTS.md and CLAUDE.md ownership and deployment as declared. Preserve literal XML examples inside inline code,
transport envelopes, tool schemas, generated protocol data, output templates, and human documentation in their own
formats. Classify exclusions by actual role; never exempt a directory merely because conversion is difficult.

### Chosen implementation

Extend the existing Python validation boundary under `agent-harness/quality/evaluations`. Apply test-first development,
the single responsibility principle, and functional core/imperative shell: pure document inspection, then repository
discovery, link resolution, diagnostics, and test integration. Reuse the current violation data type and callers where
their responsibilities still fit. Remove obsolete XML helpers after migrating callers; add no compatibility aliases,
dual-format acceptance, opt-out, rule engine, or per-consumer validator.

Choose a wrapper around [markdown-it-py](https://markdown-it-py.readthedocs.io/en/latest/using.html), using CommonMark
with table and strikethrough recognition enabled so unsupported structures cannot degrade silently into prose. This
extends an established parser through an allowed-token contract. A custom regex parser cannot reliably classify nested
Markdown; consuming a private Node evaluation package would introduce an unnecessary registry and runtime dependency.
Provide required Python dependencies through the existing Nix test environment and only other environments that import
the validator. Use no pip, venv, or uv. Verify package availability from the repository's pinned nixpkgs before wiring.

### Accepted document grammar

Accept optional valid YAML mapping frontmatter followed by one or more sibling, nonempty `###` headings, each followed
by nonempty prose paragraphs. Accept plain text, inline code, inline links, and soft line breaks inside those
paragraphs. Keep imperative prose and inline ordered steps. Require the entire document and every nonblank source line
to belong to the accepted grammar, including content after a valid section. Keep literal angle delimiters in inline
code. Require unique, nonempty heading anchors.

Reject unsupported headings, empty sections, XML or HTML authoring, emphasis, images, lists, tables, fences, indented
code, blockquotes, thematic breaks, hard breaks, and reference definitions through positive structural validation. Keep
the parser able to recognize those forms; disabling their syntax can make invalid input appear to be allowed text. Test
escaped literals, underscore-heavy names, trailing invalid content, malformed frontmatter, BOM, and CRLF.

Retain the 120-character prose wrap, 20 prose lines per section, 150 prose lines per instruction file, and independent
200 physical-line file limit. Exclude heading lines, YAML metadata, and blank separators from prose counts, retaining
the current long-literal exception. Preserve the existing description, identity, and context-byte budgets. Markdown
spacing replaces XML delimiter rules; it does not authorize looser prose or a larger context budget. Keep the existing
metadata-only core fragment valid as metadata, and validate its assembled instruction body separately.

### Link contract and deployment boundary

Replace actual XML section references with descriptive Markdown links to their owning sections. Resolve same-file and
cross-file links, encoded fragments, Unicode headings, duplicates, and missing targets. Use the
[GitHub heading-anchor convention](https://github.com/Flet/github-slugger), checked against renderer evidence. The
implementation packages the Python port of github-slugger rather than inventing an anchor algorithm. All 78 upstream
[fixtures](https://github.com/martinheidegger/github_slugger/blob/python/tests/fixtures.json) passed against the built
dependency. Do not introduce network crawling.

Validate links both from canonical source and every supported deployed location. A source-relative link can break when
Nix copies a skill to another store directory or assembles global policy, so establish projection fixtures before bulk
conversion. Extend existing skill and prompt assembly only where a moved destination requires link rebasing; keep
rewriting at the build boundary and preserve canonical ownership. Source-only paths, nonexistent sibling skills, and
absolute paths tied to one machine cannot satisfy deployed-link acceptance. Template links need an existing target, with
an anchor only when the template actually has that heading; templates do not inherit the instruction grammar.

Use source-to-deployed directory and file mappings at those existing assembly boundaries. The focused projection test
proves why the original source-relative link fails through an installed skill symlink and verifies that rebasing repairs
it. Preserve the existing global-policy and skill destinations rather than moving their owners.

### Deterministic coverage and resource bound

Extend `instruction_surface_scanner.py`, `ai_instruction_format.py`, `ai_instruction_repository_format.py`,
`ai_instruction_references.py`, and `instruction_surface_prose.py` at their existing responsibilities. Add focused
positive and negative fixtures, repository-wide enforcement, discovery coverage, and source/deployment link tests.
Update XML section extractors and literal assertions in Python, Nix checks, and behavioral YAML while retaining every
behavioral assertion. Validate generated core skills, all-skills indexes, concatenated project instructions, interactive
policy, and other owned prompt fragments through their actual generators rather than only scanning Markdown files.

Require all valid fixtures to pass and every invalid fixture to produce file, line, and expected-form diagnostics. Prove
rejection before and after a valid section, check wrong and duplicate anchors, and distinguish metadata fragments from
empty instruction files. Keep public checks meaningful without private sources and verify the additional private
inventory locally. Cache each linked document within one validation pass; introduce no daemon or polling. Measure the
observed corpus and a doubled synthetic corpus; target at most two seconds and 128 MiB for one corpus validation on the
development machine, recording environment and any justified revision before accepting the implementation.

### Milestone 1: contracts and parser

Complete in commit `29f1cd16f7d6d303eaba3cefbe193c27582e6d74`, based on
`6afe8880b3ed160f446c4c3dd64fd888812abed1`. The 73 new parser/link/projection tests and 29 existing corpus tests passed
together. The exact commit review found no findings across all six lenses. The kira rebuild succeeded and installed
parser dependencies imported successfully. At head `18dc529d4165ef69418c908f73e4f14362ba8903`,
[tests](https://github.com/Castrozan/.dotfiles/actions/runs/34313084288),
[Nix](https://github.com/Castrozan/.dotfiles/actions/runs/34313084307),
[evals](https://github.com/Castrozan/.dotfiles/actions/runs/34313084282), and
[reports](https://github.com/Castrozan/.dotfiles/actions/runs/34313084316) succeeded.

Nix built the parser environment and pinned anchor dependency. Synthetic runs with 97 and 194 maximal-prose documents
took 0.491 and 0.904 seconds, with 22.3 MiB peak RSS on kira. This preparatory commit retained the XML corpus gate; the
final gate must not accept both formats. Value is a tested replacement and a verified link-rebasing boundary.

### Milestone 2: atomic format switch

Integrated by the steward onto shipped Herdr revision `d74ecbcd8787be101bc08d5206d77eb336133baa` as
`befb62c1`, `2a4edd84`, and `a4bc3674b0421d5ab896225b0835ffa0515780b4`. Range comparison with the three original
commits in [PR 147](https://github.com/Castrozan/.dotfiles/pull/147) found only provenance-trailer changes. The private
instructions and five verbatim output templates were published in their owning repository before the public branch.
Keep the integrated Herdr changes in every subsequent rebuild; earlier divergent rebuilds replaced its live wrapper.

The source inventory is now 103 files. Normalized word comparison preserves every non-authoring body except the explicit
phrase introducing three formerly fenced shell commands; inline literal comparison preserves every non-authoring
literal. YAML metadata values are unchanged. The four authoring-policy changes were reviewed sentence by sentence.
Fleet guidance preserves its original 24 sections in three ordered chapters. Two owned steward directives now have
Markdown source files. The last source validation took 1.175 seconds wall time and 23.3 MiB peak RSS on kira.

Nix projects skills, core and index skills, project instructions, five harness interactive prompts, and steward
directives through the positive parser and link-rebasing boundary. The obsolete XML validator is removed. Hermes keeps
its YAML settings and installs the routed Humanize chapter on launch. Three owned workflows serialize dynamic input as
literal JSON and retain their models, schemas, and call ceilings. Research schemas and source prompts are assembled at
build time because its runner forbids imports and its authored files must stay below 200 lines.

Integrated main passed [tests](https://github.com/Castrozan/.dotfiles/actions/runs/34365775476),
[Nix and lint](https://github.com/Castrozan/.dotfiles/actions/runs/34365775561), and
[report deployment](https://github.com/Castrozan/.dotfiles/actions/runs/34365775473). Python recorded 3,773 unit passes
and 570 integration passes with four integration skips; QML, Lua, and quick checks passed. Nix covers 209 generated
instruction files and deployed links, translated subagents, Hermes configuration, and the assembled research workflow.
The lint expression, 201-line test file, and XML report counter failures are fixed. The exact task commits received
inline review through all six lenses. Behavioral evidence remains a separate failing gate.

### Local execution constraint

The human requested cancellation of the current CI run and prohibited the local test suite. The latest runs had already
completed successfully when checked, so no run remained to cancel. No local suite has run since that instruction.
Preserve earlier evidence and continue through rebuild, manual inspection, and CI. Before the stop, the workflow and
budget files passed 10 tests, Hermes deployment passed two, and projection passed five; subsequent test changes run in
CI. Recovery files under `/tmp/dotfiles-minimal-markdown-*` include private source snapshots and must stay private.

### Milestone 3: deployed behavior

In progress. Recorded Codex session `01a084d3-5467-7be1-b4ac-c5233a61047d` received Markdown interactive policy and
project instructions, loaded the deployed authoring skill, produced a conforming two-section draft, and corrected an
XML-plus-bold draft. Fresh Claude session `4cb184ff-3388-41c4-abd8-dc51bf6e0ced` loaded the authoring and Humanize
skills and produced Markdown drafts for both probes. Its replies also included surrounding explanations.

Fresh OpenCode session `ses_f7b28b262ffemY5ETdZe3BGZgK` loaded both skills and produced a Markdown draft. Its malformed
probe attempted an edit despite the read-only request; the edit failed because the requested original text was absent,
and no file changed. This is a failed behavioral probe, not proof that Markdown caused the behavior. Do not report
all-harness behavioral success. Further evidence must distinguish model behavior from a migration regression.

Hermes launched successfully and installed Markdown core, interactive policy, and the routed Humanize reference, with
both tool hooks preserved. Pi is absent on kira; its generated deployment is covered in Nix checks. Resume or compaction
behavior and host-specific runtime evidence beyond kira remain unverified. The three disposable probe panes were
closed; the shared Herdr server and existing fleet remained running.

These probes describe their recorded deployment. A later inspection found XML installed again. Verify current files
after rebuilding integrated main, including the Herdr compatibility wrapper and running server. Record that evidence in
[PR 147](https://github.com/Castrozan/.dotfiles/pull/147); a successful rebuild exit alone does not prove adoption.

### Milestone 4: behavioral evidence and delivery

Pending. The [eval gate](https://github.com/Castrozan/.dotfiles/actions/runs/34365775717) reports 151 stale evaluations
and 59 current evaluations against a required floor of 210. The current subset passed 53 of 59; recorded full results
are 187 of 210. The baseline remains unchanged. The human has been asked whether to keep local evaluations stopped or
refresh only those 151 affected cases; no answer has arrived. Do not run them without an explicit answer permitting it.
Never change scores, fingerprints, evidence floors, or thresholds to clear this gate.

Finish current deployment and behavioral verification. Any permitted baseline refresh must use the existing
affected-result workflow and retain measured failures and provenance.
Publish verification through the migration tracker and PR with direct browser URLs; private evidence stays private.
Continue the normal format, explicit staging, commit review, rebuild, and fast-forward publication sequence. Wait for
all consequential CI verdicts through background watchers while independent work continues.

### Completion and recovery

Completion requires the full accepted corpus and generated surfaces to use minimal Markdown, strict format and link
tests to reject deviations, preserved prose and policy semantics, unchanged non-format gates, successful rebuilds, green
required CI, and verified installed behavior. A syntax pass alone cannot prove meaning or runtime adoption. Track each
milestone's status, task commits, source revisions, verification results, and direct delivery URLs here as work
proceeds. Planning publication is not implementation delivery.
