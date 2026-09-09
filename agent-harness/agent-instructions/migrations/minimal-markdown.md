### Goal and launch boundary

Migrate dotfiles-owned AI instructions from XML sections to minimal Markdown, preserve their prose and behavior, and
make deterministic tests reject every document outside the accepted format. Deploy the result through the existing Nix
owners across Claude Code, Codex, OpenCode, Pi, and Hermes wherever each supports the surface. This canonical tracker
records the integrated implementation and incomplete behavioral verification.

### Starting evidence

Investigation started at public revision `1b594e0c5c72d53fd4d1befbc7f8f9cb5da193cb`. The existing scanner found 97
instruction files: 78 public and 19 private, containing 636 standalone opening XML sections and 59 inline XML section
references. These are an observed inventory, not fixed acceptance counts. Three focused format, structure, and prose
test files passed all 29 tests before implementation.

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

Commit `29f1cd16f7d6d303eaba3cefbe193c27582e6d74` added 73 parser, link, and projection tests; they passed with all 29
existing corpus tests. Review found no findings across six lenses. The kira rebuild and all four CI workflows at
`18dc529d4165ef69418c908f73e4f14362ba8903` passed;
[tests](https://github.com/Castrozan/.dotfiles/actions/runs/34313084288) retain the mechanical evidence.

The built parser and anchor dependency processed 97 and 194 maximal-prose documents in 0.491 and 0.904 seconds, with
22.3 MiB peak RSS on kira. The final source corpus took 1.175 seconds and 23.3 MiB, within the declared resource bound.

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
source files.

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

The human prohibited local ordinary test suites and then authorized Codex behavioral evaluations. No ordinary suite has
run since the prohibition. The earlier cancellation found no active CI run. Recovery files contain private snapshots;
keep raw transcripts and private artifacts off public remotes.

### Milestone 3: deployed behavior

Fresh and resumed Codex session `01a084d3-5467-7be1-b4ac-c5233a61047d` loaded the deployed authoring skill, produced
minimal Markdown, and corrected XML-plus-bold input. This proves skill reload and drafting, not replacement of
historical global instructions or compaction behavior. Fresh Claude session `4cb184ff-3388-41c4-abd8-dc51bf6e0ced`
loaded authoring and Humanize and drafted Markdown for both probes, with surrounding explanations.

OpenCode session `ses_f7b28b262ffemY5ETdZe3BGZgK` loaded both skills and drafted Markdown. Its malformed probe attempted
an edit despite the read-only request; the tool rejected the absent original text, and no file changed. That behavioral
probe failed; it does not establish a Markdown regression or all-harness behavioral success.

Hermes launched with Markdown core, interactive policy, the Humanize reference, and both hooks; model responses remain
unverified. Pi is absent on kira; Nix checks cover its projection. Runtime beyond kira remains unverified. All owned
probe panes were closed. [PR 147](https://github.com/Castrozan/.dotfiles/pull/147) was closed after verifying steward
integration of its three migration patches. Later deployed inspection is recorded with delivery verification below.

### Milestone 4: Codex evaluation fixes

The initial run recorded 131 passes, 18 assertion failures, and two repeated timeouts. Fixes bind provider invocations
to the active isolated worktree, pass the original request to judges, and preserve complete verdict reasons. Knowledge
and routing fixtures disable tools when testing supplied instructions; the five desktop cases now pass with zero tool
calls. Rubrics preserve required behavior while removing unsupported literal and workflow assumptions.

Judge calibration improved from 30/34 at low reasoning to 32/34 at high; both rejected all 17 known failures. Reader
recovery improved from 7/10 to 10/10. Subjects remain Codex `gpt-5.6-sol` high; Codex `gpt-5.6-luna` judges at high,
with unchanged 120-second deadlines, two workers, strict Markdown rejection, and pass-rate floors.

Humanize now audits source facts and actual representation, checks hazard ordering through prohibitions, and removes
unneeded speaker introductions. Herdr requires isolated concurrent editors; RIL distinguishes held from completed
captures and preparation from adoption. The private skill rejected during rebuild now uses minimal Markdown and
preserves both literal templates byte-for-byte. These behavior corrections are separate from the format-only migration.

### Final Codex measurements

The full run measured 188/211 passes, then affected refreshes measured 45/48 and 35/38, all without invocation errors. A
fixed three-attempt diagnostic still passed only 1/3 on incident recommendations; two answers omitted certificate
rotation timing. Humanize's existing evidence rule now explicitly covers recommendations, observed state, scope, timing,
and missing evidence. The correction uses no incident-specific terms or values.

Communication's fixed three repetitions passed 45/48 observations and 15/16 cases under the existing majority rule. The
incident case passed 1/3 before and after the recommendation correction, so these runs do not demonstrate an
improvement. Its fixture now explicitly requests the self-contained handoff and action-first order already required by
its unchanged rubric. Reader recovery now passes 22/22 after clarifying that relevant statistical consequences are part
of the requested explanation. The baseline records 200/211 passes, eleven assertion failures, and current evidence for
all 211 cases. All 20 original failed or timed-out cases pass their current fixtures.

Fifteen communication cases retain three samples each; the revised incident request has one fresh observation. Every
remaining failure stays visible in the committed baseline. Model and fixture changes prevent a causal comparison with
earlier runs; passing CI floors does not establish complete behavioral compliance.

### Delivery verification

The kira rebuild at `14382b41` and inspection of eleven deployed instruction files and links passed; both private
templates retained their hashes. [PR 147](https://github.com/Castrozan/.dotfiles/pull/147) records the final source
rebuild, installed inspection, and CI verdicts. No ordinary local test suite or Herdr server activation is authorized
for this follow-up. Raw diagnostic transcripts remain private; publish only aggregate evidence and the baseline.

### Completion and recovery

Completion requires minimal Markdown across the accepted corpus and generated surfaces, strict format and link checks,
preserved prose and policy semantics, unchanged non-format gates, successful rebuilds, green CI, and verified installed
behavior. Syntax alone cannot prove meaning or adoption. Track milestone status, task commits, source revisions,
verification results, and direct delivery URLs here.
