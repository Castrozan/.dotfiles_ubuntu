### Goal and launch boundary

Migrate dotfiles-owned AI instructions from XML sections to minimal Markdown, preserve their prose and behavior, and
make deterministic tests reject every document outside the accepted format. Deploy the result through the existing Nix
owners across Claude Code, Codex, OpenCode, Pi, and Hermes wherever each supports the surface. This canonical tracker
records the integrated implementation and incomplete behavioral verification.

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
cross-file links, encoded fragments, Unicode headings, duplicates, and missing targets. Use the [GitHub heading-anchor
convention](https://github.com/Flet/github-slugger), checked against renderer evidence. The implementation packages the
Python port of github-slugger rather than inventing an anchor algorithm. All 78 upstream
[fixtures](https://github.com/martinheidegger/github_slugger/blob/python/tests/fixtures.json) passed against the built
dependency. Do not introduce network crawling.

Validate links both from canonical source and every supported deployed location. A source-relative link can break when
Nix copies a skill to another store directory or assembles global policy, so establish projection fixtures before bulk
conversion. Extend existing skill and prompt assembly only where a moved destination requires link rebasing; keep
rewriting at the build boundary and preserve canonical ownership. Source-only paths, nonexistent sibling skills, and
absolute paths tied to one machine cannot satisfy deployed-link acceptance. Template links need an existing target, with
an anchor only when the template actually has that heading; templates do not inherit the instruction grammar.

Source-to-deployed mappings live at existing assembly boundaries. An installed-symlink fixture proves the original
relative link fails and rebasing repairs it. Global-policy and skill destinations remain unchanged.

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

Complete in commit `29f1cd16f7d6d303eaba3cefbe193c27582e6d74`, based on `6afe8880b3ed160f446c4c3dd64fd888812abed1`. The
73 new parser/link/projection tests and 29 existing corpus tests passed together. The exact commit review found no
findings across all six lenses. The kira rebuild succeeded and installed parser dependencies imported successfully. At
head `18dc529d4165ef69418c908f73e4f14362ba8903`,
[tests](https://github.com/Castrozan/.dotfiles/actions/runs/34313084288),
[Nix](https://github.com/Castrozan/.dotfiles/actions/runs/34313084307),
[evals](https://github.com/Castrozan/.dotfiles/actions/runs/34313084282), and
[reports](https://github.com/Castrozan/.dotfiles/actions/runs/34313084316) succeeded.

Nix built the parser environment and pinned anchor dependency. Synthetic runs with 97 and 194 maximal-prose documents
took 0.491 and 0.904 seconds, with 22.3 MiB peak RSS on kira. This preparatory commit retained the XML corpus gate; the
final gate must not accept both formats. Value is a tested replacement and a verified link-rebasing boundary.

### Milestone 2: atomic format switch

Integrated by the steward onto shipped Herdr revision `d74ecbcd8787be101bc08d5206d77eb336133baa` as `befb62c1`,
`2a4edd84`, and `a4bc3674b0421d5ab896225b0835ffa0515780b4`. Range comparison with the three original commits in [PR
147](https://github.com/Castrozan/.dotfiles/pull/147) found only provenance-trailer changes. The private instructions
and five verbatim output templates were published in their owning repository before the public branch. Keep the
integrated Herdr changes in every subsequent rebuild; earlier divergent rebuilds replaced its live wrapper.

The source inventory is now 103 files. Normalized word comparison preserves every non-authoring body except the explicit
phrase introducing three formerly fenced shell commands; inline literal comparison preserves every non-authoring
literal. YAML metadata values are unchanged. The four authoring-policy changes were reviewed sentence by sentence. Fleet
guidance preserves its original 24 sections in three ordered chapters. Two owned steward directives now have Markdown
source files. The last source validation took 1.175 seconds wall time and 23.3 MiB peak RSS on kira.

Nix projects skills, core and index skills, project instructions, five harness interactive prompts, and steward
directives through the positive parser and link-rebasing boundary. The obsolete XML validator is removed. Hermes keeps
its YAML settings and installs the routed Humanize chapter on launch. Three owned workflows serialize dynamic input as
literal JSON and retain their models, schemas, and call ceilings. Research schemas and source prompts are assembled at
build time because its runner forbids imports and its authored files must stay below 200 lines.

Integrated main passed [tests](https://github.com/Castrozan/.dotfiles/actions/runs/34365775476) and [Nix
checks](https://github.com/Castrozan/.dotfiles/actions/runs/34365775561): 3,773 unit passes, 570 integration passes,
four skips, and green QML, Lua, and quick checks. Nix covers 209 generated instruction files and deployed links,
translated subagents, Hermes configuration, and the assembled research workflow. Behavioral evidence remains separate.

### Local execution constraint

The human prohibited local test suites and later explicitly authorized the affected Codex behavioral evaluations. No
other local suite has run since that prohibition. The earlier CI cancellation request found no run still active. Before
the stop, workflow and budget files passed 10 tests, Hermes deployment two, and projection five. Later changes use CI.
Recovery files under `/tmp/dotfiles-minimal-markdown-*` include private snapshots and must stay private.

### Milestone 3: deployed behavior

In progress. Recorded Codex session `01a084d3-5467-7be1-b4ac-c5233a61047d` received Markdown interactive policy and
project instructions, loaded the deployed authoring skill, produced a conforming two-section draft, and corrected an
XML-plus-bold draft. Fresh Claude session `4cb184ff-3388-41c4-abd8-dc51bf6e0ced` loaded the authoring and Humanize
skills and produced Markdown drafts for both probes. Its replies also included surrounding explanations.

Fresh OpenCode session `ses_f7b28b262ffemY5ETdZe3BGZgK` loaded both skills and produced a Markdown draft. Its malformed
probe attempted an edit despite the read-only request; the edit failed because the requested original text was absent,
and no file changed. This is a failed behavioral probe, not proof that Markdown caused the behavior. Do not report
all-harness behavioral success. Further evidence must distinguish model behavior from a migration regression.

Hermes launched with Markdown core, interactive policy, the Humanize reference, and both hooks. Pi is absent on kira;
Nix checks cover its projection. Hermes model responses and runtime beyond kira remain unverified.

The integrated kira rebuild at `f9369160` succeeded. Inspection of 20 installed instruction files and their local links
found no issues. The Herdr compatibility wrapper, server PID 27507, and Codex PID 24153 survived unchanged; no server
activation occurred. This deployed Markdown inspection supersedes the earlier observation of installed XML.

Resuming the recorded Codex session loaded the deployed authoring skill and corrected an XML-plus-bold input to a
Markdown heading and prose. This proves skill reload and drafting on resume, not replacement of historical global
instructions or compaction behavior. All owned probe panes were closed. [PR
147](https://github.com/Castrozan/.dotfiles/pull/147) was closed after verifying that its three patches were already
integrated by the steward.

### Milestone 4: behavioral evidence and delivery

The human authorized Codex evaluations, then requested fixes. The first run recorded 131 passes, 18 assertion failures,
and two repeated timeouts; its baseline covered 208/210 cases. Only coverage failed the gate. Preserve historical
results until fresh measurements replace them.

Fixed a stale imported worktree path that sent subjects to the shared checkout. Evaluation worktrees now live under
`.worktrees`. Judges receive the original request, grade meaning against every rubric requirement, and retain complete
explanations. Regrading unchanged answers accepted 8/18 previous failures. Two knowledge fixtures now disable tools;
they measure supplied-instruction comprehension, not live investigation. The null-review fixture states the lookup
contract.

Judge calibration improved from 30/34 overall and 7/10 reader recovery at low reasoning to 32/34 and 10/10 at high. Both
rejected all 17 known failures. The subject remains `gpt-5.6-sol` at high reasoning; `gpt-5.6-luna` now judges at high
reasoning. Remeasure every case under that profile, preserving measured failures and existing score floors.

The first fresh diagnostic passed 12/20 prior failures with no timeouts. Follow-up guidance puts hazards before actions,
isolates concurrent editors, distinguishes held from completed RIL captures, and separates preparation from adoption.
Fixtures remove an obsolete workflow-only assumption, explicitly request commit syntax, make the RIL approval question
text-only, and add completed-capture coverage. Deadlines and strict Markdown rejection remain unchanged.

A rebuild rejected a newly integrated private skill. Its instruction body now preserves the original wording in minimal
Markdown, its description meets the existing cap, and both literal templates are extracted byte-for-byte. Full
projection passes; rebuild, baseline, CI, and deployed verification remain required before delivery.

### Completion and recovery

Completion requires minimal Markdown across the accepted corpus and generated surfaces, strict format and link checks,
preserved prose and policy semantics, unchanged non-format gates, successful rebuilds, green CI, and verified installed
behavior. Syntax alone cannot prove meaning or adoption. Track milestone status, task commits, source revisions,
verification results, and direct delivery URLs here.
