### Goal and launch boundary

Migrate dotfiles-owned AI instructions from XML sections to minimal Markdown, preserve their prose and behavior, and
make deterministic tests reject every document outside the accepted format. Deploy the result through the existing Nix
owners across Claude Code, Codex, OpenCode, Pi, and Hermes wherever each supports the surface. This is the canonical
implementation tracker. Planning is complete; implementation has not launched. Start execution only after the human
launches the goal prompt. Update this tracker when evidence changes the plan and remove stale claims.

### Starting evidence

Investigation started at public revision `1b594e0c5c72d53fd4d1befbc7f8f9cb5da193cb`. The existing scanner found 97
instruction files: 78 public and 19 private, containing 636 standalone opening XML sections and 59 inline XML section
references. These are an observed inventory, not fixed acceptance counts. Three focused format, structure, and prose
test files passed all 29 tests. No instruction implementation has changed. Inspect current revisions, sibling worktrees,
private submodule state, and peer work again before executing.

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
[GitHub heading-anchor convention](https://github.com/Flet/github-slugger), checked against renderer evidence. Prefer an
available maintained implementation; if no suitable Python dependency exists in the pinned environment, keep any
necessary resolver narrow and prove it against upstream fixtures before adopting it. Do not introduce network crawling.

Validate links both from canonical source and every supported deployed location. A source-relative link can break when
Nix copies a skill to another store directory or assembles global policy, so establish projection fixtures before bulk
conversion. Extend existing skill and prompt assembly only where a moved destination requires link rebasing; keep
rewriting at the build boundary and preserve canonical ownership. Source-only paths, nonexistent sibling skills, and
absolute paths tied to one machine cannot satisfy deployed-link acceptance. Template links need an existing target, with
an anchor only when the template actually has that heading; templates do not inherit the instruction grammar.

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

Pending. Record an exact source inventory, ownership classifications, section-reference mapping, generated surfaces,
private starting revision, and the dependent test callers. Establish passing baseline tests and preservation checks
before editing instructions. Add positive grammar fixtures, the parser wrapper, and Nix dependency provisioning behind
focused tests while the existing required repository gate still protects the XML corpus. This preparatory increment must
not accept both formats in the final gate. Finish with verified parser behavior and projection fixtures that settle link
handling; value is a tested replacement ready for the atomic migration.

### Milestone 2: atomic format switch

Pending; depends on milestone 1. Update the canonical instructions skill and its authoring-review references, convert
the inventoried instructions and section references, update generated output and link handling, migrate dependent
assertions, and switch the required repository gate together. Retire the XML validator paths in this same increment. Do
not publish an intermediate state where the authoring policy, source corpus, generated output, and required tests
disagree. Handle private instruction edits in their owning repository, preserving peer commits; record and publish the
exact private revision before committing its intended gitlink in the public repository.

Compare old and new instruction bodies after only declared delimiter, heading, link, and whitespace transformations.
Compare frontmatter and rendered inline literals independently. Audit exceptions sentence by sentence, preserving rule
order and meaning. Include public runtime prompts without changing agent launch or heartbeat behavior. Finish when the
entire applicable source and generated corpus passes the positive grammar and links, preservation evidence has no
unexplained differences, and the normal local rebuild and focused tests pass. Value is one coherent enforced format.

### Milestone 3: deployed behavior

Pending; depends on milestone 2. Inspect installed content after rebuild, including global policy, project entry points,
generated core/index skills, and a routed reference skill. Check actual loaded instructions in disposable fresh sessions
for Claude Code, Codex, and OpenCode; exercise Pi and Hermes surfaces where supported. Test ordinary
instruction-authoring requests and a malformed-format case, plus source-path and installed-path link traversal. Verify
resume or compaction delivery where persistent authority depends on it; a resumed old session is not evidence that new
instructions loaded. Record the exact unavailable runtime evidence rather than claiming all-harness success.

Use the available NixOS and Darwin configurations and CI evaluation checks; exercise host-specific runtime paths on
accessible configured machines where relevant. Keep existing interactive sessions and the agent fleet running. A shared
Herdr server activation still requires explicit approval and is not required by an instruction migration. Finish with
installed and observed runtime evidence for the supported matrix; value is verified deployment.

### Milestone 4: behavioral evidence and delivery

Pending; depends on milestone 3. Run the existing affected instruction, authority, routing, and prose-behavior evals
against real instructions. Keep syntax results separate from semantic results. Inspect failures before updating any
measurement. Follow the existing baseline policy: do not proactively re-save the full baseline after instruction edits;
if its CI gate fails, use the existing affected-result workflow and preserve thresholds, fingerprints, freshness,
provenance, and measured failures. Never edit recorded scores or weaken assertions to clear the migration.

For every increment, format owned files, stage explicit paths, commit, review the exact substantive task commits,
rebuild, then push only a fast-forward. Start a background watcher for every consequential CI run and inspect all
available failure logs before fixing the batch. Do independent work while runs execute; do not report completion before
the required verdicts are green. Leave divergent history and gitlink conflicts to the steward unless explicitly
authorized otherwise. Publish verification evidence through the existing report owner or the appropriate repository,
with direct browser URLs; private evidence remains private. Value is a delivered, reviewable migration.

### Completion and recovery

Completion requires the full accepted corpus and generated surfaces to use minimal Markdown, strict format and link
tests to reject deviations, preserved prose and policy semantics, unchanged non-format gates, successful rebuilds, green
required CI, and verified installed behavior. A syntax pass alone cannot prove meaning or runtime adoption. Track each
milestone's status, task commits, source revisions, verification results, and direct delivery URLs here as work
proceeds. Keep implementation unlaunched until the human starts the goal; planning publication is not delivery.
